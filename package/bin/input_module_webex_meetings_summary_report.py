import json
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import *

from webex_constants import (
    _MEETING_USAGE_REPORTS_ENDPOINT,
    _MEETING_ATTENDEE_REPORTS_ENDPOINT,
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
    opt_site_url = helper.get_arg('site_url')

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
    
    # check the checkpoint
    # get startdate from checkpoint
    last_timestamp_checkpoint_key = "{}_meeting_report_last_timestamp".format(
        helper.get_input_stanza_names()
    )
    timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
    #timestamp = None
    helper.log_debug("[-] last time timestamp: {}".format(timestamp))

    # set up start time
    # first time start_time from UI
    if timestamp is None:
        start_time = opt_start_time
        # save the UI start_time as checkpoint
        helper.save_check_point(
            last_timestamp_checkpoint_key, start_time
        )
        helper.log_debug("[-] no checkpoint timestamp exists, saving new timestamp: {}".format(start_time))

    else:
        # shift 1 second to avoid duplicate
        start_time = (
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    # set up end time
    now = datetime.now(timezone.utc)
    # add 24hr delay
    now_delay = now - timedelta(hours=24)

    if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) < now_delay:
        end_time = opt_end_time
    else:
        end_time = now_delay.strftime("%Y-%m-%dT%H:%M:%SZ")

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

    # construct the request params for meetings endpoint
    meeting_usage_reports_params = {"siteUrl": opt_site_url}
    meeting_usage_reports_params["from"] = start_time
    meeting_usage_reports_params["to"] = end_time
    helper.log_debug("[-] starting the ingestion for range [{start_time} - {end_time}]".format(start_time=meeting_usage_reports_params["from"], end_time=meeting_usage_reports_params["to"]))

    # fetching the meetings data
    meeting_usage_reports = paging_get_request_to_webex(
        helper,
        base_endpoint,
        _MEETING_USAGE_REPORTS_ENDPOINT,
        access_token,
        refresh_token,
        account_name,
        client_id,
        client_secret,
        meeting_usage_reports_params,
        _RESPONSE_TAG_MAP[_MEETING_USAGE_REPORTS_ENDPOINT],
    )
    helper.log_debug("[-] meeting usage reports data size: {}".format(len(meeting_usage_reports)))

    # only ingest the events that happened after the last checkpoint time
    # write meetings data into Splunk

    try:
        checkpoint_time = datetime.strptime(helper.get_check_point(last_timestamp_checkpoint_key), "%Y-%m-%dT%H:%M:%SZ")
        for meeting in meeting_usage_reports:
            # compare the meeting start time with the last checkpoint time
            last_checkpoint_time = datetime.strptime(
                helper.get_check_point(last_timestamp_checkpoint_key),
                "%Y-%m-%dT%H:%M:%SZ",
            )
            meeting_start_time = datetime.strptime(meeting["start"], "%Y-%m-%dT%H:%M:%SZ")
            # ingest the meetings that happened after the last ingestion
            if meeting_start_time > last_checkpoint_time:
                # fetching the attendees data
                try:
                    # Use meetingId as path params for attendees endpoint
                    meeting_id = meeting["meetingId"]

                    # get request params for attendees endpoint
                    attendees_params = meeting_usage_reports_params.copy()
                    # reset offset to 0 at the beginning of each meeting
                    attendees_params["offset"] = 0
                    attendees = paging_get_request_to_webex(
                        helper,
                        base_endpoint,
                        _MEETING_ATTENDEE_REPORTS_ENDPOINT.format(
                            meeting_id=meeting_id
                        ),
                        access_token,
                        refresh_token,
                        account_name,
                        client_id,
                        client_secret,
                        attendees_params,
                        _RESPONSE_TAG_MAP[_MEETING_ATTENDEE_REPORTS_ENDPOINT],
                    )
                    helper.log_debug(
                        "[-] attendees data size: {}".format(len(attendees))
                    )
                except Exception as e:
                    helper.log_error(
                        "[-] Error happened while fetching attendees data into Splunk: {}".format(
                            e
                        )
                    )
                    raise e
                try:
                    # write attendees into splunk
                    for attendee in attendees:
                        # set join_time as event timestamp
                        join_time = datetime.strptime(
                            attendee["joinedTime"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                        event_timestamp = (
                            join_time - datetime(1970, 1, 1)
                        ).total_seconds()

                        attendee_event = helper.new_event(
                            source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                            index=helper.get_output_index(),
                            sourcetype="cisco:webex:meeting:attendee:reports",
                            data=json.dumps(attendee),
                            time=event_timestamp,
                        )
                        ew.write_event(attendee_event)
                    helper.log_debug(
                        "[-] Successfully wrote {} attendees for meeting {}".format(
                            len(attendees), meeting_id
                        )
                    )
                except Exception as e:
                    helper.log_error(
                        "[-] Error happened while writing attendees data into Splunk: {}".format(
                            e
                        )
                    )
                    raise e

                # write the meeting into Splunk after all participants was successfully written to Splunk
                # set the start_time as event timestamp
                event_start_time = datetime.strptime(
                    meeting["start"], "%Y-%m-%dT%H:%M:%SZ"
                )
                event_time = (event_start_time - datetime(1970, 1, 1)).total_seconds()

                meeting_event = helper.new_event(
                    source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                    index=helper.get_output_index(),
                    sourcetype="cisco:webex:meeting:usage:reports",
                    data=json.dumps(meeting),
                    time=event_time,
                )
                ew.write_event(meeting_event)

                # save the max start_time as checkpoint for next ingestion
                checkpoint_time = max(checkpoint_time, event_start_time)
        helper.save_check_point(last_timestamp_checkpoint_key, checkpoint_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        helper.log_debug(
            "[-] Saved checkpoint: Last run time saved: {}".format(
                helper.get_check_point(last_timestamp_checkpoint_key)
            )
        )
    except Exception as e:
        helper.log_error(
            "[-] Error happened while writing data into Splunk: {}".format(e)
        )
        raise e

    



