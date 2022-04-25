import import_declare_test

import requests
from datetime import datetime, timedelta
from solnlib import conf_manager

from webex_constants import _APP_NAME, _REALM, _TOKEN_EXPIRES_CHECKPOINT_KEY, _REFRESH_TOKEN_ENDPOINT


def update_access_token(helper, account_name, client_id, client_secret, refresh_token):
    helper.log_debug("[-] Updating access token.....")
    oauth = OAuth(
        helper,
        client_id,
        client_secret,
        refresh_token,
    )
    return oauth.refresh_token(account_name)


class OAuth:
    """[summary]"""

    def __init__(
        self,
        helper,
        client_id,
        client_secret,
        refresh_token,
    ):
        """[summary]

        Args:
            helper (function): AOB helper function
            app_name (string): The name for this add-on.
            client_id (string): The client id of the Webex Oauth integration app.
            client_secret (string): The client secrete of the Webex Oauth integration app.
            refresh_token (string): The refresh token of the Webex Oauth integration app.
        """
        self.helper = helper
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token

        # dict of encripted fields
        # NOTE: MUST include all fields that need to be encripted. 
        self._password_storage_stanza = {
            "access_token": "",
            "refresh_token": "",
            "client_secret": self._client_secret,
        }
    
    def get_new_token(self):
        """
        Send a POST request to Webex Refresh token endpoint to get new access_token and refresh tokens

        Returns:
            [str, str, str]: new tokens and expiration time
        """

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": self._refresh_token,
        }

        try:
            response = requests.request("POST", _REFRESH_TOKEN_ENDPOINT, headers=headers, data=payload)
            self.helper.log_info(
                "[-] GET Access Token from Refresh Token: response.status_code: {}".format(
                    response.status_code
                )
            )
            if response.status_code != 200:
                self.helper.log_error(
                    "\t[-] Error happend while getting Access Token from Refresh Token: {}\nYou may need to re-configure the account in configuration page.".format(
                        response.text
                    )
                )
            else:
                resp = response.json()
                if resp.get("access_token"):
                    access_token = resp["access_token"]
                    refresh_token = resp["refresh_token"]
                    expires_in = resp["expires_in"]
                    return access_token, refresh_token, expires_in
        except Exception as e:
            self.helper.log_error(
                "[-] Request failed to get Access Token from Refresh Token: {}\nYou may need to re-configure the account in configuration page.".format(
                    repr(e)
                )
            )
            raise e


    def update_account_conf(self, account_name, new_account_token, new_refresh_token):
        """
        Overwrite the new tokens in the account conf/password storage endpoint
        """

        session_key = self.helper.context_meta["session_key"]

        # Create confmanger object for the app with account realm
        cfm = conf_manager.ConfManager(session_key, app=_APP_NAME , realm=_REALM)

        # Get Conf object of apps account
        account_conf = cfm.get_conf("ta_cisco_webex_add_on_for_splunk_account")

        self.helper.log_debug("[-] Updating new tokens in {} account".format(account_name))
        # NOTE: MUST include all fields that need to be encripted. 
        self._password_storage_stanza["access_token"] = new_account_token
        self._password_storage_stanza["refresh_token"] = new_refresh_token

        # NOTE: this update will take effect in next round of ingestion
        try:
            account_conf.update(account_name, self._password_storage_stanza, ["access_token", "refresh_token", "client_secret"])
        except Exception as e:
            self.helper.log_error("[-] Error happend while updating account: {}. Error: {}".format(account_name, e))
            raise e
    
    def update_expiration_checkpoint(self, account_name, new_expires_in):
        """
        Update the expiration time of the new access token in checkpoint
        """
        self.helper.log_debug("[-] Updating expiration checkpoint for {} account".format(account_name))
        try:
            # Get checpoint key
            expiration_checkpoint_key = _TOKEN_EXPIRES_CHECKPOINT_KEY.format(account_name=account_name)

            # Calculate expired time for new access token
            now = datetime.utcnow()
            delta = int(new_expires_in)
            expired_time = (now + timedelta(seconds=delta)).strftime(
                "%m/%d/%Y %H:%M:%S"
            )

            # Save checkpoint 
            self.helper.save_check_point(expiration_checkpoint_key, expired_time)
        except Exception as e:
            self.helper.log_error("[-] Error happened while saving expiration time in checkpoint : {}".format(e))
        


    def refresh_token(self, account_name):
        """
        Get the new access tokens and refresh tokens from Webex Server
        Overwrites the new tokens into  account conf/password storage endpoint
        Update the checkpoint for access token expiration time

        Returns:
            [str, str, str]: new tokens and expiration
        """
        try:
            # get new tokens from Webex server
            new_access_token, new_refresh_token, new_expires_in = self.get_new_token()
            self.helper.log_debug("[-] Successfully got new tokens")

            # update the new tokens in account conf/ password storage endpoint
            self.update_account_conf(account_name, new_access_token, new_refresh_token)

            # update checkpoint for new access_token's expired_time
            self.update_expiration_checkpoint(account_name, new_expires_in)

            return new_access_token, new_refresh_token, new_expires_in
        except Exception as e:
            self.helper.log_error("[-] Error happened while refreshing token: {}".format(e))

        return None, None, None