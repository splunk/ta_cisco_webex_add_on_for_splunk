
import import_declare_test
"""
This module will be used to get oauth token from auth code
"""

import urllib
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode
from httplib2 import Http, ProxyInfo, socks
import splunk.admin as admin
from solnlib import log
from solnlib import conf_manager
from solnlib.utils import is_true
import json
import requests


log.Logs.set_context()
logger = log.Logs().get_logger('ta_cisco_webex_add_on_for_splunk_rh_oauth2_token')

# Note: Comment L30 to get rid of the following error
# Python ERROR: AttributeError: module 'socks' has no attribute 'PROXY_TYPE_HTTP_NO_TUNNEL'
# UI ERROR: 500 Internal Server Error

# Map for available proxy type
_PROXY_TYPE_MAP = {
    'http': socks.PROXY_TYPE_HTTP,
    # 'http_no_tunnel': socks.PROXY_TYPE_HTTP_NO_TUNNEL,
    'socks4': socks.PROXY_TYPE_SOCKS4,
    'socks5': socks.PROXY_TYPE_SOCKS5,
}

"""
REST Endpoint of getting token by OAuth2 in Splunk Add-on UI Framework. T
"""


class ta_cisco_webex_add_on_for_splunk_rh_oauth2_token(admin.MConfigHandler):

    """
    This method checks which action is getting called and what parameters are required for the request.
    """

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            # Add required args in supported args
            for arg in ('url', 'method',
                        'grant_type', 'code',
                        'client_id', 'client_secret',
                        'redirect_uri'):
                self.supportedArgs.addReqArg(arg)
        return

    """
    This handler is to get access token from the auth code received
    It takes 'url', 'method', 'grant_type', 'code', 'client_id', 'client_secret', 'redirect_uri' as caller args and
    Returns the confInfo dict object in response.
    """

    def handleEdit(self, confInfo):

        try:
            logger.debug("In OAuth rest handler to get access token")
            # Get args parameters from the request
            url = self.callerArgs.data['url'][0]
            logger.debug("oAUth url %s", url)
            proxy_info = self.getProxyDetails()

            # Create payload from the arguments received
            payload = {
                'grant_type': self.callerArgs.data['grant_type'][0],
                'code': self.callerArgs.data['code'][0],
                'client_id': self.callerArgs.data['client_id'][0],
                'client_secret': self.callerArgs.data['client_secret'][0],
                'redirect_uri': self.callerArgs.data['redirect_uri'][0],
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded", }

            response = requests.request(
                "POST", url, headers=headers, data=urlencode(payload), proxies=proxy_info, verify=False
            )

            content = response.json()

            # Check for any errors in response. If no error then add the content values in confInfo
            if response.status_code == 200:
                for key, val in content.items():
                    confInfo['token'][key] = val
            else:
                # Else add the error message in the confinfo
                confInfo['token']['error'] = content['message']
            logger.info(
                "Exiting OAuth rest handler after getting access token with response %s", response.status_code)
        except Exception as exc:
            logger.exception(
                "Error occurred while getting access token using auth code")
            raise exc()

    """
    This method is to get proxy details stored in settings conf file
    """

    def getProxyDetails(self):
        # Create confmanger object for the app with realm
        cfm = conf_manager.ConfManager(self.getSessionKey(
        ), "ta_cisco_webex_add_on_for_splunk", realm="__REST_CREDENTIAL__#ta_cisco_webex_add_on_for_splunk#configs/conf-ta_cisco_webex_add_on_for_splunk_settings")
        # Get Conf object of apps settings
        conf = cfm.get_conf('ta_cisco_webex_add_on_for_splunk_settings')
        # Get proxy stanza from the settings
        proxy_config = conf.get("proxy", True)
        if not proxy_config or not is_true(proxy_config.get('proxy_enabled')):
            logger.info('Proxy is not enabled')
            return None

        url = proxy_config.get('proxy_url')
        port = proxy_config.get('proxy_port')

        if url or port:
            if not url:
                raise ValueError('Proxy "url" must not be empty')
            if not self.is_valid_port(port):
                raise ValueError(
                    'Proxy "port" must be in range [1,65535]: %s' % port
                )

        user = proxy_config.get('proxy_username')
        password = proxy_config.get('proxy_password')

        if not all((user, password)):
            logger.info('Proxy has no credentials found')
            user, password = None, None

        proxy_type = proxy_config.get('proxy_type')
        proxy_type = proxy_type.lower() if proxy_type else 'http'

        if proxy_type in _PROXY_TYPE_MAP:
            ptv = _PROXY_TYPE_MAP[proxy_type]
        elif proxy_type in _PROXY_TYPE_MAP.values():
            ptv = proxy_type
        else:
            ptv = socks.PROXY_TYPE_HTTP
            logger.info('Proxy type not found, set to "HTTP"')

        rdns = is_true(proxy_config.get('proxy_rdns'))

        proxy_info = ProxyInfo(
            proxy_host=url,
            proxy_port=int(port),
            proxy_type=ptv,
            proxy_user=user,
            proxy_pass=password,
            proxy_rdns=rdns
        )
        return proxy_info

    """
    Method to check if the given port is valid or not
    :param port: port number to be validated
    :type port: ``int``
    """

    def is_valid_port(self, port):
        try:
            return 0 < int(port) <= 65535
        except ValueError:
            return False

if __name__ == "__main__":
    admin.init(ta_cisco_webex_add_on_for_splunk_rh_oauth2_token, admin.CONTEXT_APP_AND_USER)