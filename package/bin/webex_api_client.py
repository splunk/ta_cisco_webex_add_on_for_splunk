# encoding = utf-8
import import_declare_test
from datetime import datetime, timedelta, timezone

from webex_constants import _BASE_URL, _MAX_PAGE_SIZE, UNAUTHORIZED_STATUS
from oauth_helper import update_access_token
import re

def get_time_span(helper, opt_start_time, opt_end_time, input_name, last_timestamp_checkpoint_key):
    start_time = None
    end_time = None
        
    # check if the start_time arg was provided by the user
    if opt_start_time:
        # get the last timestamp saved
        last_timestamp = helper.get_check_point(last_timestamp_checkpoint_key)
        helper.log_debug(f"[-] Last timestamp recorded for {input_name}: {last_timestamp}")
        
        if last_timestamp is None:
            start_time = opt_start_time
        else:
            # add 1 more second to avoid duplicates
            start_time = (
                datetime.strptime(last_timestamp, "%Y-%m-%dT%H:%M:%SZ") + timedelta(seconds=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            
        # set up end time
        now = datetime.now(timezone.utc)

        if opt_end_time and datetime.strptime(opt_end_time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) < now:
            end_time = opt_end_time
        else:
            end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
            
        if datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ") > datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ"):
            helper.log_info(f"[-] Finished ingestion for {input_name} for time range {start_time} - {end_time}")
            return None, None
        
        return start_time, end_time

def extract_link_regex(link_header_string):
    """
    Extracts the URL from a Link header-like string using regex.
    """
    match = re.search(r'<([^>]+)>;', link_header_string)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Next page link string does not match expected link header format: '{link_header_string}'")

def paging_get_request_to_webex(
    helper,
    base_endpoint,
    endpoint,
    access_token,
    refresh_token,
    account_name,
    client_id,
    client_secret,
    params,
    response_tag,
    is_custom_endpoint=False
):
    results = []
    # set the page_size
    params["max"] = _MAX_PAGE_SIZE if not params.get("max") else params["max"]

    paging = True
    next_page_link = None
    try:
        while paging:
            helper.log_debug("[-] next_page_link {}".format(next_page_link))
            data,response_header = make_get_request_to_webex(
                helper,
                base_endpoint,
                endpoint,
                access_token,
                refresh_token,
                account_name,
                client_id,
                client_secret,
                params,
                next_page_link,
                is_custom_endpoint=is_custom_endpoint
            )

            if data is None or len(data)==0:
                break

            # append paging data
            results.extend(data.get(response_tag))

            next_page_link_header = response_header.get("link", None)
            helper.log_debug("[--] next_page_link_header {}".format(next_page_link_header))

            if next_page_link_header:
                try:
                    next_page_link=extract_link_regex(next_page_link_header)
                    helper.log_debug("[--] next_page_link {}".format(next_page_link))
                except ValueError as e:
                    helper.log_error(f"Next page link extraction failed (regex): {e}")
            else:
                helper.log_debug("[--] This is the last page for {}".format(endpoint))
                paging = False
        return results
    except Exception as e:
        helper.log_error(
            "[-] Paging request failed to get data from webex {} API: {}".format(
                endpoint, repr(e)
            )
        )
        raise e


def make_get_request_to_webex(
    helper,
    base_endpoint,
    endpoint,
    access_token,
    refresh_token,
    account_name,
    client_id,
    client_secret,
    params,
    next_page_link,
    retry=True,
    is_custom_endpoint=False
):
    if next_page_link:
        url = next_page_link
        params = None
    else:
        url = _BASE_URL.format(base_endpoint=base_endpoint) + endpoint
        
        # reconstruct the url for meeting/qualities and cdr_feed endpoints
        if not is_custom_endpoint and (endpoint == "meeting/qualities" or endpoint == "cdr_feed"):
            protocol, rest = url.split("//")
            url = f"{protocol}//analytics.{rest}"
       
    helper.log_debug("[-] url: {} -- params: {}".format(url, params))
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=access_token),
    }

    try:
        # response = requests.request("GET", url, headers=headers, params=params)
        # use helper.send_http_request to have proxy enabled
        response = helper.send_http_request(
            url,
            "GET",
            parameters=params,
            payload=None,
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

        data = None
        if response.status_code != 200:
            helper.log_error(
                "[-] Error happened while getting date from webex {} API: code: {} - body: {}\n[!] You need to re-configure the account in configuration page".format(
                    response.url, response.status_code, response.text
                )
            )
            # refresh the expired/invalid access token
            # Add retry to avoid infinity loop
            if response.status_code == UNAUTHORIZED_STATUS and retry:
                helper.log_info("[-] Unauthorized message: {}".format(response.text))
                try:
                    helper.log_debug(
                        "[-] Refreshing the expired/invalid access token"
                    )
                    # get the latest refresh_token
                    refresh_token = helper.get_arg("global_account").get(
                        "refresh_token"
                    )
                    (
                        new_access_token,
                        new_refresh_token,
                        new_expires_in,
                    ) = update_access_token(
                        helper,
                        account_name,
                        client_id,
                        client_secret,
                        refresh_token,
                        base_endpoint
                    )
                except Exception as e:
                    helper.log_error(
                        "[-] Error happened while updating access token in endpoint-{}: {}".format(
                            endpoint, e
                        )
                    )
                    raise e

                # get webex users using new access token
                make_get_request_to_webex(
                    helper,
                    base_endpoint,
                    endpoint,
                    new_access_token,
                    new_refresh_token,
                    account_name,
                    client_id,
                    client_secret,
                    params,
                    retry=False,
                    is_custom_endpoint=False
                )

        else:
            data = response.json()
        return data, response.headers
    except Exception as e:
        helper.log_error(
            "[-] Request failed to get date from webex {} API: {}".format(
                endpoint, repr(e)
            )
        )
        raise e