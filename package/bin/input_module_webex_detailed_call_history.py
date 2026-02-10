from datetime import datetime, timedelta
import json

from webex_constants import (
    _RESPONSE_TAG_MAP,
    _GET_DETAILED_CALL_HISTORY
)
from webex_api_client import paging_get_request_to_webex
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span, change_date_format
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
    opt_start_time = change_date_format(helper.get_arg('start_time'), "%Y-%m-%dT%H:%M:%SZ" ,"%Y-%m-%dT%H:%M:%S.%fZ")
    opt_end_time = change_date_format(helper.get_arg('end_time'), "%Y-%m-%dT%H:%M:%SZ" ,"%Y-%m-%dT%H:%M:%S.%fZ")
    opt_locations = helper.get_arg('locations')

    # Get account info
    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    stored_access_token = opt_global_account.get("access_token")
    stored_refresh_token = opt_global_account.get("refresh_token")
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

    start_time, end_time = get_time_span(opt_start_time, opt_end_time, timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    #  if start and end time are not returned it means it has completed the ingestion
    if not start_time and not end_time:
        helper.log_info(
            "[-] Finished ingestion for time range {start_time} - {end_time}".format(
                start_time=opt_start_time, end_time=opt_end_time
            )
        )
        return
    
    # subtract 5 minutes to avoid errors from the API
    if not opt_end_time:
        end_time = (datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]+'Z'

    call_params["startTime"] = start_time
    call_params["endTime"] = end_time
    call_params["locations"] = opt_locations
    call_params["max"] = 500
    
    helper.log_info("[-] starting the ingestion [Webex_Detailed_Calls_History] for range [{start_time} - {end_time}]".format(start_time=call_params["startTime"], end_time=call_params["endTime"]))

    access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint)

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