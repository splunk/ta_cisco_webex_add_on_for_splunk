
# encoding = utf-8

import os
import sys
import time
import datetime

from oauth_helper import update_access_token
from webex_constants import _TOKEN_EXPIRES_CHECKPOINT_KEY

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

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # start_time = definition.parameters.get('start_time', None)
    # end_time = definition.parameters.get('end_time', None)
    pass

def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_start_time = helper.get_arg('start_time')
    opt_end_time = helper.get_arg('end_time')
    # In single instance mode, to get arguments of a particular input, use
    opt_start_time = helper.get_arg('start_time', stanza_name)
    opt_end_time = helper.get_arg('end_time', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_userdefined_global_var = helper.get_global_setting("userdefined_global_var")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''
    helper.log_debug("[-] Start collect_events...")
    # Get params 
    opt_start_time = helper.get_arg("start_time")
    opt_end_time = helper.get_arg("end_time") 
    helper.log_debug(f"[-] opt_start_time: {opt_start_time}")
    helper.log_debug(f"[-] opt_end_time: {opt_end_time}")

    # Get account info
    opt_global_account = helper.get_arg("global_account")
    account_name = opt_global_account.get("name")
    client_id = opt_global_account.get("client_id")
    client_secret = opt_global_account.get("client_secret")
    access_token = opt_global_account.get("access_token")
    refresh_token = opt_global_account.get("refresh_token")
    helper.log_debug(f"[-] account_name: {account_name}")
    helper.log_debug(f"[-] client_id: {client_id}")
    helper.log_debug(f"[-] client_secret: {client_secret}")
    helper.log_debug(f"[-] access_token: {access_token}")
    helper.log_debug(f"[-] refresh_token: {refresh_token}")

    # Get proxy
    proxy = helper.get_proxy()
    helper.log_debug(f"[-] proxy: {proxy}")
    if proxy:
        if proxy.get('proxy_username', None) and proxy.get('proxy_password', None):
            proxies = {
                "https": "{protocol}://{user}:{password}@{host}:{port}".format(protocol=proxy['proxy_type'], user=proxy['proxy_username'], password=proxy['proxy_password'], host=proxy['proxy_url'], port=proxy['proxy_port']),
                "http": "{protocol}://{user}:{password}@{host}:{port}".format(protocol=proxy['proxy_type'], user=proxy['proxy_username'], password=proxy['proxy_password'], host=proxy['proxy_url'], port=proxy['proxy_port'])
            }
        else:
            proxies = {
                "https": "{protocol}://{host}:{port}".format(protocol=proxy['proxy_type'], host=proxy['proxy_url'], port=proxy['proxy_port']),
                "http": "{protocol}://{host}:{port}".format(protocol=proxy['proxy_type'], host=proxy['proxy_url'], port=proxy['proxy_port'])
            }
    else:
        proxies = None
    helper.log_debug(f"[-] proxies: {proxies}")

    helper.log_debug("===============")

    new_access_token, new_refresh_token, new_expires_in = update_access_token(helper, account_name, client_id, client_secret, refresh_token, proxies)
    helper.log_debug(f"[*] new_access_token: {new_access_token}")
    helper.log_debug(f"[*] new_refresh_token: {new_refresh_token}")
    helper.log_debug(f"[*] new_expires_in: {new_expires_in}")