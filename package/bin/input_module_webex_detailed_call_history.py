from datetime import datetime, timedelta, timezone
import time
import json

from webex_constants import (
    _RESPONSE_TAG_MAP,
    _GET_DETAILED_CALL_HISTORY,
    _GET_LIVE_STREAM_DETAILED_CALL_HISTORY
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

    # Clamp end_time to now-1min — cdr_stream records are available 1 minute after the call data reaches the Webex Calling cloud.
    end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    one_min_ago_dt = now - timedelta(minutes=1)
    if end_dt > one_min_ago_dt:
        end_time = one_min_ago_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        end_dt = one_min_ago_dt

    access_token, refresh_token = get_valid_access_token(
        helper, account_name, client_id, client_secret,
        stored_access_token, stored_refresh_token, base_endpoint
    )
    account_region = "gov" if is_gov_account == "1" else opt_webex_account_region

    # This input pulls Detailed Call History from two complementary Webex APIs and
    # switches between them automatically based on how old the data being collected is:
    #
    #   • cdr_feed   (history)   — can query any 12-hour window between 5 minutes ago
    #                              and 30 days ago.  Used to backfill older records in
    #                              efficient 12-hour chunks.
    #   • cdr_stream (real-time) — records are available 1 minute after the call data
    #                              reaches the Webex Calling cloud but a start time
    #                              older than 12 hours is rejected; only 2 hours of
    #                              records can be pulled per request.  Used for the
    #                              most recent data once the collection window has
    #                              caught up to near real-time.
    #
    # Both endpoints return the same records, so the switch point only needs to move
    # to cdr_stream *early enough* that a start time never ages past cdr_stream's
    # 12-hour hard limit.  A chunk is served by cdr_stream once its start time is
    # within STREAM_THRESHOLD_HOURS (2 h) of now; anything older is served by cdr_feed
    # in 12-hour chunks, capped at the switch boundary so cdr_stream cleanly takes over
    # the recent remainder.  The 2-hour boundary leaves ~10 hours of slack below the
    # 12-hour limit, so even a long-running backfill (whose captured `now` drifts as
    # wall-clock advances across the per-chunk sleeps) cannot push a cdr_stream start
    # past 12 hours.
    #
    # Rate limits (identical for both endpoints, enforced here):
    #   • 1 initial request per minute   → sleep 60 s between chunks
    #   • 10 pagination requests/minute  → handled inside paging_get_request_to_webex
    #     via max_pagination_per_minute=10
    #
    # Late-data buffer (cdr_feed only): empty chunks whose end time falls within this
    # window of now are NOT advanced in the checkpoint, so server-side processing
    # delays are retried on the next run.  cdr_stream does not use this buffer because
    # it backfills late records itself.
    STREAM_THRESHOLD_HOURS = 2
    FEED_CHUNK_HOURS = 12
    STREAM_CHUNK_HOURS = 2
    LATE_DATA_BUFFER_HOURS = 2

    stream_boundary_dt = now - timedelta(hours=STREAM_THRESHOLD_HOURS)

    chunk_start_dt = start_dt
    is_first_chunk = True

    while chunk_start_dt < end_dt:
        # Choose the endpoint for this chunk based on how recent its start time is.
        use_stream = chunk_start_dt >= stream_boundary_dt

        if use_stream:
            endpoint = _GET_LIVE_STREAM_DETAILED_CALL_HISTORY
            chunk_end_dt = min(chunk_start_dt + timedelta(hours=STREAM_CHUNK_HOURS), end_dt)
        else:
            endpoint = _GET_DETAILED_CALL_HISTORY
            # Cap the cdr_feed chunk at the switch boundary so cdr_stream handles the
            # recent remainder rather than cdr_feed reaching into near-real-time data.
            chunk_end_dt = min(
                chunk_start_dt + timedelta(hours=FEED_CHUNK_HOURS),
                stream_boundary_dt,
                end_dt,
            )

        chunk_start = chunk_start_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
        chunk_end = chunk_end_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

        if not is_first_chunk:
            helper.log_info(
                "[-] Waiting 60 s before next chunk to comply with "
                "Webex CDR rate limit (1 initial request/minute)"
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
            "[-] starting the ingestion [Webex_Detailed_Calls_History] using {} "
            "for range [{} - {}]".format(endpoint, chunk_start, chunk_end)
        )

        calls = paging_get_request_to_webex(
            helper,
            base_endpoint,
            endpoint,
            access_token,
            refresh_token,
            account_name,
            client_id,
            client_secret,
            call_params,
            _RESPONSE_TAG_MAP[endpoint],
            is_custom_endpoint=False,
            webex_account_region=account_region,
            max_pagination_per_minute=10,
        )

        helper.log_debug("[-] detailed call history response size: {} for {} chunk [{} - {}]".format(len(calls), endpoint, chunk_start, chunk_end))

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
                        endpoint, chunk_start, chunk_end, e
                    )
                )
                raise e

        if chunk_last_report_time is not None:
            # Chunk had data — the max Report time always wins, for both cdr_feed and
            # cdr_stream.  The checkpoint-advance logic below only applies to empty chunks.
            helper.save_check_point(last_timestamp_checkpoint_key, chunk_last_report_time)
            helper.log_debug("[-] Checkpoint saved: {} after {} chunk [{} - {}]".format(chunk_last_report_time, endpoint, chunk_start, chunk_end))
        elif use_stream:
            # Empty cdr_stream chunk — advance the checkpoint to the chunk end.
            helper.save_check_point(last_timestamp_checkpoint_key, chunk_end)
            helper.log_debug("[-] Checkpoint advanced (empty cdr_stream): {} after chunk [{} - {}]".format(chunk_end, chunk_start, chunk_end))
        else:
            buffer_boundary_dt = now - timedelta(hours=LATE_DATA_BUFFER_HOURS)

            if chunk_end_dt <= buffer_boundary_dt:
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