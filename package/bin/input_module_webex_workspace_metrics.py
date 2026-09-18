from oauth_helper import get_valid_access_token, get_account_oauth_config
from webex_utils import get_time_span
from webex_api_client import paging_get_request_to_webex
from webex_contact_center_utils import *
from webex_constants import (
   _LIST_WORKSPACES_ENDPOINT,
   _WORKSPACES_METRICS_ENDPOINT,
   _RESPONSE_TAG_MAP
)

def collect_events(helper, ew):
   # Account args
   opt_global_account = helper.get_arg("global_account")
   account_name = opt_global_account.get("name")
   base_endpoint = opt_global_account.get("endpoint")
   client_id, client_secret, stored_access_token, stored_refresh_token, auth_type = get_account_oauth_config(opt_global_account)
   
   # Input args
   opt_start_time = helper.get_arg("start_time")
   opt_end_time = helper.get_arg("end_time")
   opt_metrics = helper.get_arg("metrics")
   opt_org_id = helper.get_arg("org_id")
   
   params = {}
   
   if opt_org_id:
      params["orgId"] = opt_org_id
   
   # Checkpoint key name
   last_timestamp_checkpoint_key = "{}_workspace_metrics_timestamp".format(
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
   
   access_token, refresh_token = get_valid_access_token(helper, account_name, client_id, client_secret, stored_access_token, stored_refresh_token, base_endpoint, auth_type)

   helper.log_info("[-] starting the ingestion [Workspace Metrics] for range [{start_time} - {end_time}]".format(start_time=start_time, end_time=start_time))

   try:
      # List all workspaces
      workspaces = paging_get_request_to_webex(
         helper,
         base_endpoint,
         _LIST_WORKSPACES_ENDPOINT,
         access_token,
         refresh_token,
         account_name,
         client_id,
         client_secret,
         params,
         _RESPONSE_TAG_MAP[_LIST_WORKSPACES_ENDPOINT],
         is_custom_endpoint=False,
      )
      
      if not workspaces:
         helper.log_info("[-] No workspaces found for the account {}".format(account_name))
         return
         
      # Construct the request params for workspace metrics endpoint
      metrics_params = {}
      
      #iterate over workspaces and save all the ids
      workspace_ids = []
      
      for workspace in workspaces:
         workspace_ids.append(workspace.get("id"))
      
      metrics_results = []
      
      #retrieve metrics for each workspace
      for workspace_id in workspace_ids:
         metrics_names = opt_metrics.split(",")
         
         metrics_params["workspaceId"] = workspace_id
         metrics_params["from"] = start_time
         metrics_params["to"] = end_time
         metrics_params["metricName"] = metrics_names
         
         metrics_data = paging_get_request_to_webex(
            helper,
            base_endpoint,
            _WORKSPACES_METRICS_ENDPOINT,
            access_token,
            refresh_token,
            account_name,
            client_id,
            client_secret,
            metrics_params,
            _RESPONSE_TAG_MAP[_WORKSPACES_METRICS_ENDPOINT],
            is_custom_endpoint=False,
         )
         
         if not metrics_data:
            helper.log_info("[-] No metrics data found for workspace id {}".format(workspace_id))
            continue
            
         # collect every result
         metrics_results += metrics_data
      
      # write events into Splunk
      for metrics in metrics_results:
            event = helper.new_event(
               source=helper.get_input_type() + "://" + helper.get_input_stanza_names(),
               data=json.dumps(metrics),
               index=helper.get_output_index(),
               sourcetype="cisco:webex:workspace:metrics",
            )
            ew.write_event(event)
   except Exception as e:
      helper.log_error(
         "[-] Error happened while getting workspace metrics: {}".format(e)
      )
      raise e
   
   
   