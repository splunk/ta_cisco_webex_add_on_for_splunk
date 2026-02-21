import json
from datetime import datetime, timezone
from webex_api_client import paging_get_request_to_webex
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span

from webex_constants import (
   _FEDRAMP_BASE_URL,
   _START_TIME_FIELDS
)

# Handle Webex API date formats %Y-%m-%dT%H:%M:%SZ - "%Y-%m-%dT%H:%M:%S.%fZ"
def parse_date_to_ts(string_date):
    if string_date.endswith("Z"):
        string_date = string_date[:-1]
        dt = datetime.fromisoformat(string_date).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(string_date)
    return int(dt.timestamp())

def collect_events(helper, ew):
        
        input_name = helper.get_input_stanza_names()
        
        # account args
        opt_global_account = helper.get_arg("global_account")
        account_name = opt_global_account.get("name")
        client_id = opt_global_account.get("client_id")
        client_secret = opt_global_account.get("client_secret")
        stored_access_token = opt_global_account.get("access_token")
        stored_refresh_token = opt_global_account.get("refresh_token")
        base_endpoint = opt_global_account.get("endpoint")
        is_gov_account = opt_global_account.get("is_gov_account")
        
        # input args
        opt_start_time = helper.get_arg("start_time")
        opt_end_time = helper.get_arg("end_time")
        opt_webex_endpoint = helper.get_arg("webex_endpoint")
        opt_webex_base_url = helper.get_arg("webex_base_url")
        opt_method = helper.get_arg("method")
        opt_query_params = helper.get_arg("query_params")
        opt_request_body = helper.get_arg("request_body")
        
        start_time = None
        end_time = None
        
        last_run_timestamp_checkpoint_key = f"{input_name}_webex_generic_endpoint_input_last_timestamp"
        last_run_timestamp = helper.get_check_point(last_run_timestamp_checkpoint_key)
          
        # retrieve the start and end time according to the checkpoiting logic
        start_time, end_time = get_time_span(opt_start_time, opt_end_time, last_run_timestamp)
        
        # check if there is a value for the start and end time, otherwise don't do anything
        if not start_time and not end_time:
            helper.log_info(f"[-] Finished ingestion for {input_name} for time range {start_time} - {end_time}.")
            return
        
        helper.log_debug(f"[-] Using start_time: {start_time} and end_time: {end_time}.")
        
        # get a valid access token    
        access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint)
        
        # assign the Webex base API depending on the type of account
        webex_base_url = _FEDRAMP_BASE_URL if is_gov_account else opt_webex_base_url
        
        try:
            # query params object
            query_params = {}
                        
            # add params if they exist
            if opt_query_params:
                
                # remove space and/or commas at the end of the string
                query_string = opt_query_params.rstrip()
                query_string = query_string[:-1] if query_string.endswith(",") else query_string
                 
                query_params = {key.strip(): value.strip() for item in query_string.split(",") for key, value in [item.split("=")]}
                
            if start_time and end_time:
                query_params.update({"from": start_time, "to": end_time})
            
            # request body
            payload = None

            # add reqeust body if they exist
            if opt_request_body:
                payload = json.loads(opt_request_body)

            
            # get the data
            data = paging_get_request_to_webex(
                helper,
                webex_base_url,
                opt_webex_endpoint,
                access_token,
                refresh_token,
                account_name,
                client_id,
                client_secret,
                query_params,
                "items",
                is_custom_endpoint=True,
                method=opt_method,
                payload=payload

            )
            
            # used to save the last "end time" registered in the reponse
            last_item_timestamp = 0
            
            # iterate and save into Splunk each item of the result
            for item in data:
                
                event_start_time = datetime.now(timezone.utc)
                
                for key in _START_TIME_FIELDS:
                    if key in item:
                        event_start_time = parse_date_to_ts(item[key])
                        break
                
                # if the start/create time from the event is earlier than the last run time, it is a duplicate, so ignore it.
                if last_run_timestamp and event_start_time <= parse_date_to_ts(last_run_timestamp):
                    continue
                
                normalized_sourcetype = opt_webex_endpoint.replace("/",":")
                
                event = helper.new_event(
                                index=helper.get_output_index(),
                                sourcetype=f"cisco:webex:{normalized_sourcetype}",
                                time=event_start_time,
                                data=json.dumps(item)
                )
                ew.write_event(event)
                
                # keep track of the timestamp on each event to update the last_item_timestamp variable, which will be used for checkpointing.
                if event_start_time > last_item_timestamp:
                    last_item_timestamp = event_start_time
                    formatted_time = datetime.fromtimestamp(last_item_timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    helper.save_check_point(last_run_timestamp_checkpoint_key, formatted_time)
            
            # log the saved checkpoint time, if it doesn't exist then save the end time as the checkpoint
            if last_item_timestamp:
                formatted_time = datetime.fromtimestamp(last_item_timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                helper.log_debug(f"[-] Saved checkpoint — latest event time: {formatted_time}.")
            else:
                helper.save_check_point(last_run_timestamp_checkpoint_key, end_time)
                helper.log_debug(f"[-] Saved checkpoint - end time: {end_time}.")
            
            helper.log_info(f"Execution for {input_name} completed.")
        except Exception as e:
            helper.log_error(f"[-] Error happened while hitting {opt_webex_endpoint} endpoint.")
            raise e