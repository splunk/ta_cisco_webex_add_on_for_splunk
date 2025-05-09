# encoding = utf-8
import import_declare_test

from webex_constants import _BASE_URL, _MAX_PAGE_SIZE, UNAUTHORIZED_STATUS
from oauth_helper import update_access_token
import re

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
):
    results = []
    # set the page_size
    params["max"] = _MAX_PAGE_SIZE if not params.get("max") else params["max"]

    paging = True
    try:
        while paging:
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
            )

            if data is None or len(data)==0:
                break

            # append paging data
            results.extend(data.get(response_tag))

            next_page_link = response_header.get("link", None)
            helper.log_debug("[--] next_page_link {}".format(next_page_link))

            if next_page_link:
                # update offset to get the next page
                if "offset" in next_page_link:
                    offset = int(params.get("offset", 0)) + len(data.get(response_tag))
                    params["offset"] = offset
                else:
                    # Regular expression to find the cursor value
                    # This will capture characters following 'cursor=' until it hits either '&' or the end of the string
                    match = re.search(r'cursor=([^&>]+)', next_page_link)
                    # Extract the cursor value if it is found
                    if match:
                        cursor_value = match.group(1)
                        params["cursor"] = cursor_value
                    else:
                        raise Exception("Cursor value not found for next page")
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
    retry=True,
):
    url = _BASE_URL.format(base_endpoint=base_endpoint) + endpoint

    # reconstruct the url for meeting/qualities and cdr_feed endpoints
    if endpoint == "meeting/qualities" or endpoint == "cdr_feed":
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
                )

        else:
            data = response.json()
        return data, response.headers
    except Exception as e:
        helper.log_error(
            "[-] Request failed to get date from webex {} API: {}".format(
                response.url, repr(e)
            )
        )
        raise e