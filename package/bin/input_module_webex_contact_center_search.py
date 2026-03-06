import json
import re
from oauth_helper import get_valid_access_token
from webex_utils import get_time_span, to_epoch_ms

from webex_constants import (
   _Webex_Contact_Center_BASE_URL
)


def extract_nested_list(response):
   data_content = response.get("data", {})
   first_level_val = next(iter(data_content.values()), {})
   events = next(iter(first_level_val.values()), [])
   return events

def prepare_paginated_query(query_str):
    # Remove any existing hardcoded pagination blocks to start fresh
    query_str = re.sub(r',?\s*pagination\s*:\s*\{[^}]+\}', '', query_str)

    # Update the Query Header (Variable Definitions)
    # Adds '$cursor: String' inside the query(...) parentheses
    if '$cursor' not in query_str:
        query_str = re.sub(
            r'query\s*\(([^)]+)\)',
            r'query (\1, $cursor: String)',
            query_str
        )

    # Update the Data Object (Arguments) with 'pagination: { cursor: $cursor })'
    if 'pagination' not in query_str:
        query_str = re.sub(
            r'(\b(?!query\b)\w+\s*\([^)]+)\)',
            r'\1, pagination: { cursor: $cursor })',
            query_str
        )

    # Universal PageInfo Injection
    if 'pageInfo' not in query_str:
        # Matches the main object and the first inner list block
        query_str = re.sub(
            r'(\w+\s*\{)(\s*\w+\s*\{[^{}]*\})',
            r'\1\2\n    pageInfo {\n      hasNextPage\n      endCursor\n    }',
            query_str
        )

    # Final Cleanup: Fix double commas or spaces caused by regex
    query_str = query_str.replace(', ,', ',').replace('(,', '(').strip()

    return query_str


def find_key_recursive(obj, target_key):
   """
   Recursively searches for a key in a nested dictionary/list structure.
   Returns the value of the key if found, otherwise returns None.
   """
   if isinstance(obj, dict):
      #Check if the key is at the current level
      if target_key in obj:
         return obj[target_key]
      #If not, drill down into each value
      for value in obj.values():
         result = find_key_recursive(value, target_key)
         if result is not None:
               return result
   elif isinstance(obj, list):
      #If it's a list, check each item in the list
      for item in obj:
         result = find_key_recursive(item, target_key)
         if result is not None:
               return result
   return None



def collect_events(helper, ew):
   input_name = helper.get_input_stanza_names()

   # Account args
   opt_global_account = helper.get_arg("global_account")
   account_name = opt_global_account.get("name")
   client_id = opt_global_account.get("client_id")
   client_secret = opt_global_account.get("client_secret")
   stored_access_token = opt_global_account.get("access_token")
   stored_refresh_token = opt_global_account.get("refresh_token")
   base_endpoint = opt_global_account.get("endpoint")

   
   # Input args
   opt_start_time = helper.get_arg("start_time")
   opt_end_time = helper.get_arg("end_time")
   opt_webex_contact_center_region = helper.get_arg("webex_contact_center_region")
   opt_org_id = helper.get_arg("org_id")
   opt_method = helper.get_arg("method")
   opt_query = helper.get_arg("query")
   helper.log_debug(f"[-] opt_query: {opt_query}")


   # Construct the url 
   webex_contact_center_base_url = _Webex_Contact_Center_BASE_URL.format(region=opt_webex_contact_center_region)
   url = f"https://{webex_contact_center_base_url}/search"
   params = {"orgId": opt_org_id}

   # Construct the headers
   access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint)
   headers = {
        "Authorization": f"Bearer {access_token}"
   }

   # Define the variables
   start_time = None
   end_time = None
   
   last_run_timestamp_checkpoint_key = f"{input_name}_webex_contact_center_search_input_last_timestamp"
   last_run_timestamp = helper.get_check_point(last_run_timestamp_checkpoint_key)
      
   # retrieve the start and end time according to the checkpoiting logic
   start_time, end_time = get_time_span(opt_start_time, opt_end_time, last_run_timestamp, "%Y-%m-%dT%H:%M:%SZ")
   
   # check if there is a value for the start and end time, otherwise don't do anything
   if not start_time and not end_time:
      helper.log_info(f"[-] Finished ingestion for {input_name} for time range {start_time} - {end_time}.")
      return
   
   helper.log_debug(f"[-] Using start_time: {start_time} and end_time: {end_time}.")
   
   variables = {
      'from': to_epoch_ms(start_time),
      'to': to_epoch_ms(end_time)
   }

   # Construct the payload
   payload = {
      'query': prepare_paginated_query(opt_query),
      'variables': variables
   }

   try:
      has_next = True
      all_events = []
      while has_next:
         # use helper.send_http_request to have proxy enabled
         response = helper.send_http_request(
            url,
            "POST",
            parameters=params,
            payload=payload,
            headers=headers,
            cookies=None,
            verify=False,
            cert=None,
            timeout=30,
            use_proxy=True,
         )
         helper.log_debug(
            "[-] GET data from webex {} API: response.status_code: {}".format(
                  response.url,
                  response.status_code,
            )
         )
         helper.log_debug(f"[-] Request method: {response.request.method}, Request body: {response.request.body}")

         data = None
         if response.status_code != 200:
            helper.log_error(
                  "[-] Error happened while getting date from webex {} API: code: {} - body: {}".format(
                     response.url, response.status_code, response.text
                  )
            )
            break
         else:
            resp = response.json()
            # Extract the list of events
            events = extract_nested_list(resp)
            helper.log_debug(f"[-] Found {len(events)} events in current page")
            all_events.extend(events)

            # Extract pageInfo
            page_info = find_key_recursive(resp, "pageInfo")
            helper.log_debug(f"[-] page_info: {page_info}")
            has_next = page_info.get("hasNextPage", False)

            if has_next:
               payload["variables"]["cursor"] = page_info.get("endCursor")
            else:
               helper.log_debug("[-] Reached the last page.")
      helper.log_debug(f"[-] Fetched {len(all_events)} data for input {input_name} for time range [{start_time} - {end_time}]")

      # write data into Splunk
      if all_events:
         for item in all_events:
            event = helper.new_event(
               index=helper.get_output_index(),
               sourcetype="cisco:webex:contact:center",
               data=json.dumps(item)
            )
            ew.write_event(event)
         # save the end_time as the checkpoint only after data has been successfully retrieved and ingested into Splunk
         helper.log_debug(f"[-] Ingested {len(all_events)} data for input {input_name} for time range [{start_time} - {end_time}]")
         if all_events:
            helper.save_check_point(last_run_timestamp_checkpoint_key, end_time)
            helper.log_debug(f"[-] Saved checkpoint - end time: {end_time}.")
   except Exception as e:
      helper.log_error("[-] Request failed to get date from webex {} API: {}".format(url, repr(e)))
      raise e