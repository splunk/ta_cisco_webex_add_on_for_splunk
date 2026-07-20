import json
import time

from oauth_helper import get_valid_access_token
from webex_api_client import paging_get_request_to_webex
from webex_constants import _APP_NAME


def _parse_json_arg(raw_value, arg_name):
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as e:
        raise ValueError(f"{arg_name} is not valid JSON: {e}")
    if not isinstance(parsed, dict):
        raise ValueError(f"{arg_name} must be a JSON object, got {type(parsed).__name__}.")
    return parsed


def collect_events(helper, ew):
    input_name = helper.get_input_stanza_names()

    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    stored_access_token = opt_global_account.get("access_token")
    stored_refresh_token = opt_global_account.get("refresh_token")
    base_endpoint = opt_global_account.get("endpoint")

    access_token, refresh_token = get_valid_access_token(
        helper, account_name, client_id, client_secret,
        stored_access_token, stored_refresh_token, base_endpoint,
    )

    base_url = helper.get_arg("webex_base_url")
    webex_endpoint = helper.get_arg("webex_endpoint")
    sourcetype = helper.get_arg("sourcetype")
    method = helper.get_arg("method")
    index = helper.get_arg("index")
    raw_params = helper.get_arg("query_params") or "{}"
    raw_request_body = helper.get_arg("request_body") or "{}"

    try:
        query_params = _parse_json_arg(raw_params, "query_params")
        request_body = _parse_json_arg(raw_request_body, "request_body")
    except ValueError as e:
        helper.log_error(f"Invalid configuration for input '{input_name}': {e}")
        return

    # Sortable batch identifier — epoch milliseconds.
    batch_id = str(int(time.time() * 1000))
    batch_time = time.time()

    helper.log_info(
        f"Starting Webex inventory fetch for input '{input_name}' "
        f"(endpoint={webex_endpoint}, batch_id={batch_id})."
    )

    try:
        items = paging_get_request_to_webex(
            helper,
            base_url,
            webex_endpoint,
            access_token,
            refresh_token,
            account_name,
            client_id,
            client_secret,
            query_params,
            "items",
            method=method,
            payload=request_body or None,
        )
        helper.log_info(f"Fetched {len(items)} items from Webex endpoint '{webex_endpoint}' for input '{input_name}' (batch_id={batch_id}).")
    except Exception as e:
        helper.log_error(
            f"Collection failed for input '{input_name}' (batch_id={batch_id}): {e}. "
        )
        return

    for item in items:
        event_data = dict(item)
        event_data["batch_id"] = batch_id
        event_data["webex_endpoint"] = webex_endpoint

        event = helper.new_event(
            source=helper.get_input_type(),
            index=index,
            sourcetype=sourcetype,
            data=json.dumps(event_data, ensure_ascii=False, default=str),
            time=batch_time,
        )
        ew.write_event(event)

    helper.log_info(
        f"Successfully indexed {len(items)} records for input '{input_name}' "
        f"(endpoint={webex_endpoint}, batch_id={batch_id})."
    )