import json
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import *

from webex_constants import (
    _MEETINGS_ENDPOINT,
    _GET_MEETING_QUALITIES,
    _RESPONSE_TAG_MAP
)
from webex_api_client import paging_get_request_to_webex
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span

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

    # check the checkpoint
    # get start time from checkpoint
    last_timestamp_checkpoint_key = "{}_meeting_qualities_last_timestamp".format(
        helper.get_input_stanza_names()
    )

    timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
    helper.log_debug("[-] last time timestamp: {}".format(timestamp))

    start_time, end_time = get_time_span(opt_start_time, opt_end_time, timestamp, "%Y-%m-%dT%H:%M:%SZ")

    #  if start and end time are not returned it means it has completed the ingestion
    if not start_time and not end_time:
        helper.log_info(
            "[-] Finished ingestion for time range {start_time} - {end_time}".format(
                start_time=opt_start_time, end_time=opt_end_time
            )
        )
        return

    access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint)

    # get meeting ids from the list meetings endpoint
    # construct the request params for meetings endpoint
    meetings_params = {"meetingType":"meeting", "state": "ended"}
    meetings_params["from"] = start_time
    meetings_params["to"] = end_time
    helper.log_debug("[-] starting the ingestion for range [{start_time} - {end_time}]".format(start_time=meetings_params["from"], end_time=meetings_params["to"]))
    
    meetings = paging_get_request_to_webex(
        helper,
        base_endpoint,
        _MEETINGS_ENDPOINT,
        access_token,
        refresh_token,
        account_name,
        client_id,
        client_secret,
        meetings_params,
        _RESPONSE_TAG_MAP[_MEETINGS_ENDPOINT],
    )
    
    helper.log_debug("[-] meetings data size: {}".format(len(meetings)))

    # retrieve the meeting qualities data for each meeting
    latest_time = None
    
    for meeting in meetings:
        # only ingest the meetings that happened after the last checkpoint time
        # compare the meeting start time with the last checkpoint time
        last_checkpoint_time = opt_start_time if not helper.get_check_point(last_timestamp_checkpoint_key) else helper.get_check_point(last_timestamp_checkpoint_key)
        last_checkpoint_time = datetime.strptime(last_checkpoint_time,"%Y-%m-%dT%H:%M:%SZ")
        meeting_start_time = datetime.strptime(meeting["start"], "%Y-%m-%dT%H:%M:%SZ")
        helper.log_debug("[-] meeting_start_time: {} vs last_checkpoint_time: {}".format(meeting_start_time, last_checkpoint_time))

        if meeting_start_time > last_checkpoint_time and meeting.get("id", None):
            meetings_qualities_params = {"meetingId": meeting["id"], "max": 1000}
            meetings_qualities_data_list = paging_get_request_to_webex(
                helper,
                base_endpoint,
                _GET_MEETING_QUALITIES,
                access_token,
                refresh_token,
                account_name,
                client_id,
                client_secret,
                meetings_qualities_params,
                _RESPONSE_TAG_MAP[_GET_MEETING_QUALITIES],
            )
            helper.log_debug("[-] meetings qualities data list size: {} for meeting: {}".format(len(meetings_qualities_data_list), meeting["id"]))

            if len(meetings_qualities_data_list) > 0:
                # write the meeting qualities data into Splunk
                try:
                    for meetings_quality in meetings_qualities_data_list:
                        # set the joinTime as event timestamp
                        event_start_time = datetime.strptime(meetings_quality["joinTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                        event_time = (event_start_time - datetime(1970, 1, 1)).total_seconds()

                        meeting_quality_event = helper.new_event(
                            source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                            index=helper.get_output_index(),
                            sourcetype="cisco:webex:meeting:qualities",
                            data=json.dumps(meetings_quality),
                            time=event_time,
                        )
                        ew.write_event(meeting_quality_event)
                except Exception as e:
                    helper.log_error("[-] Error happened while writing meetings qualities into Splunk: {}".format(e))
                    raise e
                latest_time = last_checkpoint_time if latest_time is None else latest_time
                latest_time = max(latest_time, meeting_start_time)

    # save the latest meeting start time as checkpoint for next ingestion
    if latest_time:
        helper.save_check_point(last_timestamp_checkpoint_key, latest_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        helper.log_debug("[-] Saved checkpoint: Last run time saved: {}".format(helper.get_check_point(last_timestamp_checkpoint_key)))