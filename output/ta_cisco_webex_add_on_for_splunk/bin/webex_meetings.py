import import_declare_test
import sys
import json

from splunklib import modularinput as smi

import os
import traceback
import requests
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from solnlib.modular_input import checkpointer
from splunktaucclib.modinput_wrapper import base_modinput  as base_mi 

bin_dir  = os.path.basename(__file__)
app_name = os.path.basename(os.path.dirname(os.getcwd()))

class ModInputWEBEX_MEETINGS(base_mi.BaseModInput): 

    def __init__(self):
        use_single_instance = False
        super(ModInputWEBEX_MEETINGS, self).__init__(app_name, "webex_meetings", use_single_instance) 
        self.global_checkbox_fields = None

    def get_scheme(self):
        scheme = smi.Scheme('webex_meetings')
        scheme.description = 'Webex Meetings'
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(
            smi.Argument(
                'name',
                title='Name',
                description='Name',
                required_on_create=True
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'global_account',
                required_on_create=True,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'start_time',
                required_on_create=False,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                'end_time',
                required_on_create=False,
            )
        )
        
        return scheme

    def validate_input(self, definition):
        """validate the input stanza"""
        """Implement your own validation logic to validate the input stanza configurations"""
        pass

    def get_app_name(self):
        return "app_name" 

    def collect_events(helper, ew):

        #   Get the CloudConnect json file .cc.json
        script_name = __file__
        script_name = script_name[:-3]
        config_file_name = '.'.join([script_name, 'cc.json'])

        # Extract the url, method and headers for this input from the .cc.json file
        with open(config_file_name) as f:
            data = json.load(f)

        url    = data["requests"][0]["request"]["url"]
        method = data["requests"][0]["request"]["method"]
        headers= json.dumps(data["requests"][0]["request"]["headers"])

        # insert input values into the url and/or header (helper class handles credential store)
        opt_global_account = helper.get_arg('global_account')
        url = url.replace("{{"+'global_account'+"}}",opt_global_account)
        headers = headers.replace("{{"+'global_account'+"}}",opt_global_account)
        
        opt_start_time = helper.get_arg('start_time')
        url = url.replace("{{"+'start_time'+"}}",opt_start_time)
        headers = headers.replace("{{"+'start_time'+"}}",opt_start_time)
        
        opt_end_time = helper.get_arg('end_time')
        url = url.replace("{{"+'end_time'+"}}",opt_end_time)
        headers = headers.replace("{{"+'end_time'+"}}",opt_end_time)
        
        # Now execute the api call
        headers=json.loads(headers)
        response = helper.send_http_request(url, method, headers=headers,  parameters="", payload=None, cookies=None, verify=True, cert=None, timeout=None, use_proxy=True)

        try:
            response.raise_for_status()
            
        except:
            helper.log_error (response.text)
        
        if response.status_code == 200:
            try:
                data = json.dumps(response.json())
                sourcetype=  "webex_meetings"  + "://" + helper.get_input_stanza_names()
                event = helper.new_event(source="webex_meetings", index=helper.get_output_index(), sourcetype=sourcetype , data=data)
                ew.write_event(event)
            except:
                helper.log_info("Error inserting event")


    def get_account_fields(self):
        account_fields = []
        return account_fields


    def get_checkbox_fields(self):
        checkbox_fields = []
        return checkbox_fields


    def get_global_checkbox_fields(self):
        if self.global_checkbox_fields is None:
            checkbox_name_file = os.path.join(bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = []
            except Exception as e:
                self.log_error('Get exception when loading global checkbox parameter names. ' + str(e))
                self.global_checkbox_fields = []
        return self.global_checkbox_fields


if __name__ == '__main__':
    exit_code = ModInputWEBEX_MEETINGS().run(sys.argv)
    sys.exit(exit_code)


