import json
from datetime import datetime, timezone
from webex_api_client import paging_get_request_to_webex
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span

from webex_constants import (
   _FEDRAMP_BASE_URL,
   _TIME_FIELDS
)

# Handle Webex API date formats %Y-%m-%dT%H:%M:%SZ - "%Y-%m-%dT%H:%M:%S.%fZ"
def parse_start_date_to_ts(string_date):
    if string_date.endswith("Z"):
        string_date = string_date[:-1]
        dt = datetime.fromisoformat(string_date).replace(tzinfo=timezone.utc)
    else:
        dt = datetime.fromisoformat(string_date)
    return dt.timestamp()

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
        opt_query_params = helper.get_arg("query_params")
        
        start_time = None
        end_time = None
        
        last_timestamp_checkpoint_key = f"{input_name}_webex_generic_endpoint_input_last_timestamp"
        last_timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
        
        # check if the start_time arg was provided
        if opt_start_time:
            
            # retrieve the start and end time according to the checkpoiting logic
            start_time, end_time = get_time_span(opt_start_time, opt_end_time, last_timestamp)
            
            # check if there is a value for the start and end time, otherwise don't do anything
            if not start_time and not end_time:
                helper.log_info(f"[-] Finished ingestion for {input_name} for time range {start_time} - {end_time}.")
                return
            
            helper.log_debug(f"[-] Using start_time: {start_time} and end_time: {end_time}.")
        else:
            helper.log_debug("No start time was passed for this input.")
        
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
                is_custom_endpoint=True
            )
            
            # iterate and save into Splunk each item of the result
            for item in data:
                normalized_sourcetype = opt_webex_endpoint.replace("/",":")
                
                event_time = datetime.now(timezone.utc)
                
                for key in _TIME_FIELDS:
                    if key in item:
                        event_time = parse_start_date_to_ts(item[key])
                        break
                
                event = helper.new_event(
                                index=helper.get_output_index(),
                                sourcetype=f"cisco:webex:{normalized_sourcetype}",
                                time=event_time,
                                data=json.dumps(item)
                )
                ew.write_event(event)
            if end_time:
                # save the end_time of the last round as checkpoint for next ingestion
                helper.save_check_point(last_timestamp_checkpoint_key, end_time)
                helper.log_debug(f"[-] Saved checkpoint: Last run time saved: {end_time}.")
            
            helper.log_info(f"Execution for {input_name} completed.")
        except Exception as e:
            helper.log_error(f"[-] Error happened while hitting {opt_webex_endpoint} endpoint.")
            raise e