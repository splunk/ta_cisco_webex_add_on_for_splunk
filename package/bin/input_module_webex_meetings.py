import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from webex_constants import (
    _MEETINGS_ENDPOINT,
    _MEETING_PARTICIPANTS_ENDPOINT,
    _RESPONSE_TAG_MAP,
    _TOKEN_EXPIRES_CHECKPOINT_KEY,
    _LIST_PEOPLE_ENDPOINT
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

    # check the checkpoint
    # get startdate from checkpoint
    last_timestamp_checkpoint_key = "{}_meeting_report_last_timestamp".format(
        helper.get_input_stanza_names()
    )

    # construct the request params for meetings endpoint
    meetings_params = {"meetingType":"scheduledMeeting"}

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
    now = datetime.utcnow()

    if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ") < now:
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

    meetings_params["from"] = start_time
    meetings_params["to"] = end_time
    helper.log_debug("[-] starting the ingestion for range [{start_time} - {end_time}]".format(start_time=meetings_params["from"], end_time=meetings_params["to"]))

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

    # get user list
    people_params = {"max": 1000}
    users = paging_get_request_to_webex(
        helper,
        base_endpoint,
        _LIST_PEOPLE_ENDPOINT,
        access_token,
        refresh_token,
        account_name,
        client_id,
        client_secret,
        people_params,
        _RESPONSE_TAG_MAP[_LIST_PEOPLE_ENDPOINT],
    )
    helper.log_debug("[-] users data size: {}".format(len(users)))

    for user in users:
        if user.get("emails", None):
            for email in user["emails"]:
                meetings_params["hostEmail"] = email
                # fetching the meetings data for each user
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
                helper.log_debug("[-] meetings data size: {} for user: {}".format(len(meetings), email))
                # helper.log_debug("[-] meetings data for user: {}\n{}".format(email, meetings))

                # only ingest the events that happened after the last checkpoint time
                # write meetings data into Splunk
                try:
                    # checkpoint_time = datetime.strptime(helper.get_check_point(last_timestamp_checkpoint_key), "%Y-%m-%dT%H:%M:%SZ")
                    for meeting in meetings:
                        # compare the meeting start time with the last checkpoint time
                        last_checkpoint_time = datetime.strptime(
                            helper.get_check_point(last_timestamp_checkpoint_key),
                            "%Y-%m-%dT%H:%M:%SZ",
                        )
                        meeting_start_time = datetime.strptime(meeting["start"], "%Y-%m-%dT%H:%M:%SZ")

                        helper.log_debug("[-] meeting_start_time: {} vs last_checkpoint_time: {}".format(meeting_start_time, last_checkpoint_time))
                        # ingest the meetings that happened after the last ingestion
                        if meeting_start_time > last_checkpoint_time:
                            # add a custom filed for query param: hostEmail
                            meeting["query_hostEmail"] = email
                            # write the meeting into Splunk after all participants was successfully written to Splunk
                            # set the start_time as event timestamp
                            event_start_time = datetime.strptime(
                                meeting["start"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            event_time = (event_start_time - datetime(1970, 1, 1)).total_seconds()

                            meeting_event = helper.new_event(
                                source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                                index=helper.get_output_index(),
                                sourcetype="cisco:webex:meetings",
                                data=json.dumps(meeting),
                                time=event_time,
                            )
                            ew.write_event(meeting_event)
                except Exception as e:
                    helper.log_error(
                        "[-] Error happened while writing data into Splunk: {}".format(e)
                    )
                    raise e
    # save the end_time of the last round as checkpoint for next ingestion
    helper.save_check_point(last_timestamp_checkpoint_key, end_time)
    helper.log_debug("[-] Saved checkpoint: Last run time saved: {}".format(helper.get_check_point(last_timestamp_checkpoint_key)))