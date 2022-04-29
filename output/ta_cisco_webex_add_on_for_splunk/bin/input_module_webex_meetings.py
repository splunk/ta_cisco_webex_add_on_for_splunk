import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from webex_constants import (
    _MEETINGS_ENDPOINT,
    _MEETING_PARTICIPANTS_ENDPOINT,
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

    # check the checkpoint
    # get startdate from checkpoint
    last_timestamp_checkpoint_key = "{}_meeting_report_last_timestamp".format(
        helper.get_input_stanza_names()
    )

    # construct the request params for meetings endpoint
    meetings_params = {"state":"ended","meetingType":"meeting"}

    timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
    #timestamp = None
    helper.log_debug("[-] last time timestamp: {}".format(timestamp))

    # first time start_time from UI
    if timestamp is None:
        start_time = opt_start_time
        # save the UI start_time as checkpoint
        helper.save_check_point(
            last_timestamp_checkpoint_key, start_time
        )
        helper.log_debug("[-] no checkpoint timestamp exists, saving new timestamp: {}".format(start_time))

    else:
        start_time = timestamp

    meetings_params["from"] = start_time
    if opt_end_time:
        meetings_params["to"] = opt_end_time
        # compare if start_time ?> end_time, if so, break
        if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(
            opt_end_time, "%Y-%m-%dT%H:%M:%SZ"
        ):
            helper.log_info(
                "[-] Finished ingestion for time range {opt_start_time} - {opt_end_time}".format(
                    opt_start_time=opt_start_time, opt_end_time=opt_end_time
                )
            )
            return

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
            helper, account_name, client_id, client_secret, refresh_token
        )

    # fetching the meetings data
    meetings = paging_get_request_to_webex(
        helper,
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

    # only ingest the events that ended after the last checkpoint time
    # write meetings data into Splunk

    try:
        for meeting in meetings:

            # fetching the participants data
            try:
                # Use id as path params for participants endpoint
                meeting_id = meeting["id"]

                # get request params for participants endpoint
                participants_params = {}
                participants = paging_get_request_to_webex(
                    helper,
                    _MEETING_PARTICIPANTS_ENDPOINT.format(
                        meeting_id=meeting_id
                    ),
                    access_token,
                    refresh_token,
                    account_name,
                    client_id,
                    client_secret,
                    participants_params,
                    _RESPONSE_TAG_MAP[_MEETING_PARTICIPANTS_ENDPOINT],
                )
                helper.log_debug(
                    "[-] participants data size: {}".format(len(participants))
                )
            except Exception as e:
                helper.log_error(
                    "[-] Error happened while fetching participants data into Splunk: {}".format(
                        e
                    )
                )
                raise e
            try:
                # write participants into splunk
                for participant in participants:
                    # add meeting title
                    participant["meeting_title"] = meeting["title"]
                    # set join_time as event timestamp
                    join_time = datetime.strptime(
                        participant["joinedTime"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    event_timestamp = (
                        join_time - datetime(1970, 1, 1)
                    ).total_seconds()

                    participant_event = helper.new_event(
                        source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                        index=helper.get_output_index(),
                        sourcetype="cisco:webex:meetings:participant",
                        data=json.dumps(participant),
                        time=event_timestamp,
                    )
                    ew.write_event(participant_event)
                helper.log_debug(
                    "[-] Successfully wrote {} participants for meeting {}".format(
                        len(participants), meeting_id
                    )
                )
            except Exception as e:
                helper.log_error(
                    "[-] Error happened while writing participants data into Splunk: {}".format(
                        e
                    )
                )
                raise e

            # write the meeting into Splunk after all participants was successfully writtern to Splunk
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

        end_checkpoint_time = datetime.strftime(
            datetime.now() - timedelta(hours = 12),"%Y-%m-%dT%H:%M:%SZ"
        )

        helper.save_check_point(
            last_timestamp_checkpoint_key, end_checkpoint_time
        )

    except Exception as e:
        helper.log_error(
            "[-] Error happened while writing data into Splunk: {}".format(e)
        )
        raise e