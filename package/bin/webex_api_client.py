# encoding = utf-8
import import_declare_test

import time
from webex_constants import _BASE_URL, _MAX_PAGE_SIZE, UNAUTHORIZED_STATUS
from oauth_helper import update_access_token
import re

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
    is_custom_endpoint=False,
    webex_account_region="us_ca",
    method = "GET",
    payload=None,
    max_pagination_per_minute=None,
):
    """Fetch all pages from a Webex API endpoint.

    max_pagination_per_minute: when set, limits the number of pagination
    requests (requests after the initial one) to this value per 60-second
    window.  Used to comply with the CDR Feed rate limit of 10 additional
    pagination requests per minute.
    """
    results = []
    # set the page_size
    params["max"] = _MAX_PAGE_SIZE if not params.get("max") else params["max"]

    paging = True
    next_page_link = None
    pagination_count = 0   # counts requests after the initial one
    window_start = None    # start of the current 60-second pagination window
    _MAX_RETRIES = 3       # max retries per request on 429

    try:
        while paging:
            # --- pagination rate-limit gate ---
            # The initial request is handled by the caller (60 s between chunks).
            # Here we only throttle the *pagination* requests (2nd, 3rd, … page).
            if max_pagination_per_minute is not None and next_page_link is not None:
                if window_start is None:
                    window_start = time.time()

                if pagination_count >= max_pagination_per_minute:
                    elapsed = time.time() - window_start
                    if elapsed < 60:
                        sleep_secs = 60 - elapsed
                        helper.log_info(
                            "[-] Pagination rate limit ({} req/min) reached; "
                            "sleeping {:.1f} s before continuing".format(
                                max_pagination_per_minute, sleep_secs
                            )
                        )
                        time.sleep(sleep_secs)
                    pagination_count = 0
                    window_start = time.time()

            helper.log_debug("[-] next_page_link {}".format(next_page_link))

            # Retry loop for 429 responses
            for attempt in range(1, _MAX_RETRIES + 1):
                try:
                    data, response_header = make_get_request_to_webex(
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
                        is_custom_endpoint=is_custom_endpoint,
                        webex_account_region=webex_account_region,
                        method=method,
                        payload=payload
                    )
                    break  # success — exit retry loop
                except Exception as exc:
                    if attempt < _MAX_RETRIES and getattr(getattr(exc, 'response', None), 'status_code', None) == 429:
                        helper.log_warning(
                            "[-] Retrying after 429 (attempt {}/{})".format(attempt, _MAX_RETRIES)
                        )
                        continue
                    raise

            if next_page_link is not None:
                pagination_count += 1

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
    is_custom_endpoint=False,
    webex_account_region="us_ca",
    method = "GET",
    payload=None
):
    if next_page_link:
        url = next_page_link
        params = None
    else: 
        url = _BASE_URL.format(base_endpoint=base_endpoint) + endpoint
        protocol, rest = url.split("//")
        
        # reconstruct the url for meeting/qualities and cdr_feed endpoints
        if not is_custom_endpoint and endpoint == "meeting/qualities":
            if webex_account_region == "us_ca":
                url = f"{protocol}//analytics.{rest}"
            elif webex_account_region == "gov":
                url = f"{protocol}//analytics.webexgov.us/v1/meeting/qualities"
            else:
                url = f"{protocol}//analytics-{webex_account_region}.{rest}"
        elif not is_custom_endpoint and endpoint == "cdr_feed":
            #construct the URL depending on the region
            if webex_account_region == "us_ca":
                url = f"{protocol}//analytics-calling.{rest}"
            elif webex_account_region == "gov":
                url = f"{protocol}//analytics-calling-{webex_account_region}.webexapis.com/v1/cdr_feed"
            else:
                url = f"{protocol}//analytics-calling-{webex_account_region}.{rest}"
       
    helper.log_debug("[-] url: {} -- method: {} -- params: {}".format(url, method, params))
    
    headers = {
        "Authorization": "Bearer {access_token}".format(access_token=access_token),
    }

    try:
        # response = requests.request("GET", url, headers=headers, params=params)
        # use helper.send_http_request to have proxy enabled
        response = helper.send_http_request(
            url,
            method,
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
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            helper.log_warning(
                "[-] Rate limited (429) by webex {} API; sleeping {} s before retry".format(
                    endpoint, retry_after
                )
            )
            time.sleep(retry_after)
            # Re-raise so the caller (paging_get_request_to_webex) retries the request
            response.raise_for_status()
        elif response.status_code != 200:
            helper.log_error(
                "[-] Error happened while getting date from webex {} API: code: {} - body: {}\n[!] You need to re-configure the account in configuration page".format(
                    response.url, response.status_code, response.text
                )
            )
            response.raise_for_status()
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