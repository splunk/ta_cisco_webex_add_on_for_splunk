import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from webex_constants import (
    _RESPONSE_TAG_MAP,
    _TOKEN_EXPIRES_CHECKPOINT_KEY,
    _GET_DETAILED_CALL_HISTORY
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
    opt_locations = helper.get_arg('locations')

    # Get account info
    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    access_token = opt_global_account.get("access_token")
    refresh_token = opt_global_account.get("refresh_token")
    base_endpoint = opt_global_account.get("endpoint")
        
    # check the checkpoint
    # get startdate from checkpoint
    last_timestamp_checkpoint_key = "{}_detailed_call_history_last_timestamp".format(
        helper.get_input_stanza_names()
    )

    # construct the request params for meetings endpoint
    call_params = {}

    timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
    
    helper.log_debug("[-] last time timestamp: {}".format(timestamp))

    # set up start time
    # first time start_time from UI
    if timestamp is None:
        start_time = opt_start_time
    else:
        # shift 1 second to avoid duplicate
        start_time = (
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # set up end time
    now = datetime.utcnow()

    if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ") < now:
        end_time = opt_end_time
    else:
        end_time = (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # compare if start_time ?> end_time, if so, break
    if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ"):
        helper.log_info(
            "[-] Finished ingestion for time range {start_time} - {end_time}".format(
                start_time=start_time, end_time=end_time
            )
        )
        return

    call_params["startTime"] = start_time
    call_params["endTime"] = end_time
    call_params["locations"] = opt_locations
    call_params["max"] = 500
    
    helper.log_info("[-] starting the ingestion [Webex_Detailed_Calls_History] for range [{start_time} - {end_time}]".format(start_time=call_params["startTime"], end_time=call_params["endTime"]))

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


    calls = paging_get_request_to_webex(
        helper,
        base_endpoint,
        _GET_DETAILED_CALL_HISTORY,
        access_token,
        refresh_token,
        account_name,
        client_id,
        client_secret,
        call_params,
        _RESPONSE_TAG_MAP[_GET_DETAILED_CALL_HISTORY],
    )
    
    helper.log_debug("[-] detailed call history response size: {}".format(len(calls)))

    for call in calls:
        try:
            call_start_time = call["Start time"]
            
            meeting_event = helper.new_event(
                                source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                                index=helper.get_output_index(),
                                sourcetype="cisco:webex:call:detailed_history",
                                data=json.dumps(call),
                                time=call_start_time,
            )
            ew.write_event(meeting_event)
             # save the end_time of the last round as checkpoint for next ingestion
            helper.save_check_point(last_timestamp_checkpoint_key, end_time)
            helper.log_debug("[-] Saved checkpoint: Last run time saved: {}".format(helper.get_check_point(last_timestamp_checkpoint_key)))
        except Exception as e:
            helper.log_error(
                "[-] Error happened while writing data into Splunk: {}".format(e)
            )
            raise e