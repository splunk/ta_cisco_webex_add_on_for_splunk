import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from webex_constants import (
    _ORGANIZATIONS_ENDPOINT,
    _ADMIN_AUDIT_EVENTS_ENDPOINT,
    _RESPONSE_TAG_MAP,
    _TOKEN_EXPIRES_CHECKPOINT_KEY,
)
from webex_api_client import paging_get_request_to_webex
from oauth_helper import update_access_token

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def collect_events(helper, ew):

    # insert input values into the url and/or header (helper class handles credential store)
    opt_start_time = helper.get_arg('start_time')
    opt_end_time = helper.get_arg('end_time')

    # Get account info
    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    access_token = opt_global_account.get("access_token")
    refresh_token = opt_global_account.get("refresh_token")
    base_endpoint = opt_global_account.get("endpoint")

    # check if the access token expired
    # get the access_token_expired_time checkpoint
    expiration_checkpoint_key = _TOKEN_EXPIRES_CHECKPOINT_KEY.format(
        account_name=account_name
    )
    access_token_expired_time = helper.get_check_point(expiration_checkpoint_key)

    now = datetime.utcnow()

    # update the access token if it expired
    if (
        not access_token_expired_time
        or datetime.strptime(access_token_expired_time, "%m/%d/%Y %H:%M:%S") < now
    ):

        helper.log_debug(
            "[*] The access token of account {account_name} expired! Updating now!".format(
                account_name=account_name
            )
        )

        # override the access_token and expires_in
        access_token, refresh_token, expires_in = update_access_token(
            helper, account_name, client_id, client_secret, refresh_token, base_endpoint
        )
    
    # fetching org from Organizations endpoint
    try:
        orgs_params = {}
        organizations = paging_get_request_to_webex(
            helper,
            base_endpoint,
            _ORGANIZATIONS_ENDPOINT,
            access_token,
            refresh_token,
            account_name,
            client_id,
            client_secret,
            orgs_params,
            _RESPONSE_TAG_MAP[_ORGANIZATIONS_ENDPOINT],
        )
        helper.log_debug("[-] organizations size: {}".format(len(organizations)))
    except Exception as e:
            helper.log_error("[-] Error happened while hitting Organizations endpoint: {}".format(e))
            raise e

    for org in organizations:
        org_id = org["id"]

        # check the checkpoint for each org
        # get start date from checkpoint
        last_timestamp_checkpoint_key = "{}-{}_admin_audit_event_report_last_timestamp".format(
            helper.get_input_stanza_names(), org_id
        )

        # construct the request params for admin audit event endpoint
        admin_audit_event_params = {}

        timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
        helper.log_debug("[-] For orgID-{}, last time timestamp: {}".format(org_id, timestamp))

        # set up start time
        # first time start_time from UI
        if timestamp is None:
            start_time = opt_start_time
            # save the UI start_time as checkpoint
            helper.save_check_point(
                last_timestamp_checkpoint_key, start_time
            )
            helper.log_debug("[-] For orgID-{}, no checkpoint timestamp exists, saving new timestamp: {}".format(org_id, start_time))
        else:
            # shift 1 second to avoid duplicate
            start_time = (
                datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(milliseconds=1)
            ).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'

        # set up end time
        now = datetime.utcnow()
        helper.log_debug("[-] now: {}".format(now))

        if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%S.%fZ") < now:
            end_time = opt_end_time
        else:
            end_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'
        
        # compare if start_time ?> end_time, if so, break
        if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ") > datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ"):
            helper.log_info(
                "[-] Finished ingestion for orgID-{org_id} for time range {start_time} - {end_time}".format(
                    org_id=org_id, start_time=start_time, end_time=end_time
                )
            )
            return

        admin_audit_event_params["from"] = start_time
        admin_audit_event_params["to"] = end_time
        helper.log_debug("[-] starting the ingestion for orgID-{org_id} for range [{start_time} - {end_time}]".format(org_id=org_id, start_time=admin_audit_event_params["from"], end_time=admin_audit_event_params["to"]))

        # fetching the admin audit events data
        try:
            # get the audit event from a specific org
            admin_audit_event_params["orgId"] = org["id"]
            admin_audit_events = paging_get_request_to_webex(
                helper,
                base_endpoint,
                _ADMIN_AUDIT_EVENTS_ENDPOINT,
                access_token,
                refresh_token,
                account_name,
                client_id,
                client_secret,
                admin_audit_event_params,
                _RESPONSE_TAG_MAP[_ADMIN_AUDIT_EVENTS_ENDPOINT],
            )
            helper.log_debug("[-] For orgID-{}, admin audit events size: {}".format(org_id, len(admin_audit_events)))
        except Exception as e:
            helper.log_error("[-] For orgID-{}, Error happened while fetching admin audit events into Splunk: {}".format(org_id, e))
            raise e
        
        try:
            last_checkpoint_time = datetime.strptime(
                    helper.get_check_point(last_timestamp_checkpoint_key),
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                )
            # write admin audit events into splunk
            for event in admin_audit_events:
                # compare the meeting start time with the last checkpoint time
                admin_audit_event_created_time = datetime.strptime(event["created"], "%Y-%m-%dT%H:%M:%S.%fZ")
                # only ingest the events that happened after the last checkpoint time
                if admin_audit_event_created_time > last_checkpoint_time:
                    # set created time as event timestamp
                    event_timestamp = (
                        admin_audit_event_created_time - datetime(1970, 1, 1)
                    ).total_seconds()

                    admin_audit_event = helper.new_event(
                        source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                        index=helper.get_output_index(),
                        sourcetype="cisco:webex:admin:audit:events",
                        data=json.dumps(event),
                        time=event_timestamp,
                    )
                    ew.write_event(admin_audit_event)
                    # save the max created_time as checkpoint for next ingestion
                    checkpoint_time = datetime.strptime(helper.get_check_point(last_timestamp_checkpoint_key),"%Y-%m-%dT%H:%M:%S.%fZ",)
                    checkpoint_time = max(checkpoint_time, admin_audit_event_created_time)
                    helper.save_check_point(last_timestamp_checkpoint_key, checkpoint_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z')
                    helper.log_debug("[-] For orgID-{}, Saved checkpoint: Last run time saved: {}".format(org_id, helper.get_check_point(last_timestamp_checkpoint_key)))
        except Exception as e:
            helper.log_error("[-] For orgID-{}, Error happened while writing admin audit events into Splunk: {}".format(org_id, e))
            raise e