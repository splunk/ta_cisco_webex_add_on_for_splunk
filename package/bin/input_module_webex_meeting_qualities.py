import json
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import *

from webex_constants import (
    _MEETINGS_ENDPOINT,
    _GET_MEETING_QUALITIES,
    _RESPONSE_TAG_MAP,
    _TOKEN_EXPIRES_CHECKPOINT_KEY,
)
from webex_api_client import paging_get_request_to_webex
from oauth_helper import update_access_token

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

    # check the checkpoint
    # get start time from checkpoint
    last_timestamp_checkpoint_key = "{}_meeting_qualities_last_timestamp".format(
        helper.get_input_stanza_names()
    )

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
    now = datetime.now(timezone.utc)

    if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) < now:
        end_time = opt_end_time
    else:
        end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    # compare if start_time ?> end_time, if so, break
    if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(
        end_time, "%Y-%m-%dT%H:%M:%SZ"
    ):
        helper.log_info(
            "[-] Finished ingestion for time range {start_time} - {end_time}".format(
                start_time=start_time, end_time=end_time
            )
        )
        return

    # check if the access token expired
    # get the access_token_expired_time checkpoint
    expiration_checkpoint_key = _TOKEN_EXPIRES_CHECKPOINT_KEY.format(
        account_name=account_name
    )
    access_token_expired_time = helper.get_check_point(expiration_checkpoint_key)

    now = datetime.now(timezone.utc)

    # update the access token if it expired
    if (
        not access_token_expired_time
        or datetime.strptime(access_token_expired_time, "%m/%d/%Y %H:%M:%S").replace(tzinfo=timezone.utc) < now
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