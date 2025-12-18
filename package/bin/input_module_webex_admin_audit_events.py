import json
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import *

from webex_constants import (
    _ORGANIZATIONS_ENDPOINT,
    _ADMIN_AUDIT_EVENTS_ENDPOINT,
    _RESPONSE_TAG_MAP,
)
from webex_api_client import paging_get_request_to_webex
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span

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
    stored_access_token = opt_global_account.get("access_token")
    stored_refresh_token = opt_global_account.get("refresh_token")
    base_endpoint = opt_global_account.get("endpoint")

    access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint)
    
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

        # construct the request params for admin audit event endpoint
        admin_audit_event_params = {}
        
        # check the checkpoint for each org
        # get start date from checkpoint
        last_timestamp_checkpoint_key = "{}-{}_admin_audit_event_report_last_timestamp".format(
            helper.get_input_stanza_names(), org_id
        )
        timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
        helper.log_debug("[-] For orgID-{}, last time timestamp: {}".format(org_id, timestamp))

        start_time, end_time = get_time_span(opt_start_time, opt_end_time, timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        
        # if start and end time are not returned it means it has completed the ingestion
        if not start_time and not end_time:
            helper.log_info(
                "[-] Finished ingestion for orgID-{org_id} for time range {start_time} - {end_time}".format(
                    org_id=org_id, start_time=opt_start_time, end_time=opt_end_time
                )
            )
            return
        
        if timestamp is None:
            helper.save_check_point(
                last_timestamp_checkpoint_key, start_time
            )
            helper.log_debug("[-] For orgID-{}, no checkpoint timestamp exists, saving new timestamp: {}".format(org_id, start_time))

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