from datetime import datetime, timedelta, timezone
import time
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
    opt_webex_account_region = helper.get_arg('account_region')

    # Get account info
    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    stored_access_token = opt_global_account.get("access_token")
    stored_refresh_token = opt_global_account.get("refresh_token")
    base_endpoint = opt_global_account.get("endpoint")
    is_gov_account = opt_global_account.get("is_gov_account")
    
        
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

    # get_time_span() advances the checkpoint by +1 second.  CDR Report times carry
    # millisecond precision, so +1 s can create up to a 999 ms gap.  Override to +1 ms.
    if timestamp is not None and start_time is not None:
        start_time = (
            datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(milliseconds=1)
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

    #  if start and end time are not returned it means it has completed the ingestion
    if not start_time and not end_time:
        helper.log_info(
            "[-] Finished ingestion for time range {start_time} - {end_time}".format(
                start_time=opt_start_time, end_time=opt_end_time
            )
        )
        return

    now = datetime.now(timezone.utc)

    # Clamp start_time to within 30 days (API hard limit).
    thirty_days_ago_dt = now - timedelta(days=30)
    start_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    if start_dt < thirty_days_ago_dt:
        clamped_start = thirty_days_ago_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        helper.log_warning(
            "[-] Start time {} is beyond the 30-day API lookback limit. "
            "Data from {} to {} cannot be collected and will be skipped.".format(
                start_time, start_time, clamped_start
            )
        )
        start_time = clamped_start
        start_dt = thirty_days_ago_dt

    # Clamp end_time to now-5min — records are only available 5 minutes after a call ends.
    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    five_min_ago_dt = now - timedelta(minutes=5)
    if end_dt > five_min_ago_dt:
        end_time = five_min_ago_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        end_dt = five_min_ago_dt

    access_token, refresh_token = get_valid_access_token(
        helper, account_name, client_id, client_secret,
        stored_access_token, stored_refresh_token, base_endpoint
    )
    account_region = "gov" if is_gov_account == "1" else opt_webex_account_region

    # The CDR Feed API allows at most 12 hours per request.  When the total range
    # exceeds 12 hours we iterate through sequential 12-hour chunks.
    #
    # Rate limits enforced here:
    #   • 1 initial request per minute  → sleep 60 s between chunks
    #   • 10 pagination requests/minute → handled inside paging_get_request_to_webex
    #     via max_pagination_per_minute=10
    #
    # Late-data buffer: empty chunks whose end time falls within this window of now
    # are NOT advanced in the checkpoint.  Server-side processing delays may mean
    # records haven't arrived yet even though 5 minutes have passed.  The window is
    # left at the current checkpoint and retried on the next run.
    LATE_DATA_BUFFER_HOURS = 2

    chunk_start_dt = start_dt
    is_first_chunk = True

    while chunk_start_dt < end_dt:
        chunk_end_dt = min(chunk_start_dt + timedelta(hours=12), end_dt)
        chunk_start = chunk_start_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        chunk_end = chunk_end_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

        if not is_first_chunk:
            helper.log_info(
                "[-] Waiting 60 s before next chunk to comply with "
                "CDR Feed rate limit (1 initial request/minute)"
            )
            time.sleep(60)
        is_first_chunk = False

        call_params = {
            "startTime": chunk_start,
            "endTime": chunk_end,
            "locations": opt_locations,
            "max": 500,
        }

        helper.log_debug(
            "[-] starting the ingestion [Webex_Detailed_Calls_History] "
            "for range [{} - {}]".format(chunk_start, chunk_end)
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
            is_custom_endpoint=False,
            webex_account_region=account_region,
            max_pagination_per_minute=10,
        )

        helper.log_debug("[-] detailed call history response size: {} for chunk [{} - {}]".format(len(calls), chunk_start, chunk_end))

        chunk_last_report_time = None  # running max Report time seen in this chunk

        for call in calls:
            try:
                report_time_str = call["Report time"]
                call_report_time_ts = datetime.strptime(report_time_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc).timestamp()

                if chunk_last_report_time is None or report_time_str > chunk_last_report_time:
                    chunk_last_report_time = report_time_str

                meeting_event = helper.new_event(
                                    source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
                                    index=helper.get_output_index(),
                                    sourcetype="cisco:webex:call:detailed_history",
                                    data=json.dumps(call),
                                    time=call_report_time_ts,
                )

                ew.write_event(meeting_event)

            except Exception as e:
                helper.log_error(
                    "[-] Error happened while writing data into Splunk for endpoint {} chunk [{} - {}]: {}".format(
                        _GET_DETAILED_CALL_HISTORY, chunk_start, chunk_end, e
                    )
                )
                raise e

        buffer_boundary_dt = now - timedelta(hours=LATE_DATA_BUFFER_HOURS)

        if chunk_last_report_time is not None:
            # Chunk had data — save the max Report time and continue to next chunk.
            helper.save_check_point(last_timestamp_checkpoint_key, chunk_last_report_time)
            helper.log_debug("[-] Checkpoint saved: {} after chunk [{} - {}]".format(chunk_last_report_time, chunk_start, chunk_end))
        elif chunk_end_dt <= buffer_boundary_dt:
            # Empty chunk entirely outside the late-data buffer — safe to advance
            # past it since any server-side delay would have resolved by now.
            helper.save_check_point(last_timestamp_checkpoint_key, chunk_end)
            helper.log_debug("[-] Checkpoint advanced (empty, outside late-data buffer): {} after chunk [{} - {}]".format(chunk_end, chunk_start, chunk_end))
        elif chunk_start_dt < buffer_boundary_dt:
            # Empty chunk that spans the buffer boundary.  The portion before the
            # boundary is safe to skip; advance the checkpoint to the boundary so
            # the next run only re-queries the recent risky portion.
            safe_end = buffer_boundary_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
            helper.save_check_point(last_timestamp_checkpoint_key, safe_end)
            helper.log_info(
                "[-] Empty chunk [{} - {}] spans the {}-hour late-data buffer boundary; "
                "checkpoint advanced to {} (safe portion). "
                "Remaining window will be retried on next run.".format(
                    chunk_start, chunk_end, LATE_DATA_BUFFER_HOURS, safe_end
                )
            )
            break
        else:
            # Empty chunk entirely within the late-data buffer window.
            # Leave the checkpoint unchanged and stop processing.
            helper.log_info(
                "[-] Empty chunk [{} - {}] is within the {}-hour late-data buffer; "
                "checkpoint not advanced, will retry on next run.".format(
                    chunk_start, chunk_end, LATE_DATA_BUFFER_HOURS
                )
            )
            break

        # Advance by +1 ms so the next chunk's startTime does not overlap with
        # this chunk's endTime — records at the exact boundary would otherwise
        # be returned by both API calls and written as duplicates.
        chunk_start_dt = chunk_end_dt + timedelta(milliseconds=1)