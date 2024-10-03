import import_declare_test

import sys
import json
from datetime import datetime, timedelta
from splunklib import modularinput as smi

import os
import traceback
import requests
from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from solnlib.modular_input import checkpointer
from splunktaucclib.modinput_wrapper import base_modinput  as base_mi
import input_module_webex_meeting_qualities as input_module

bin_dir  = os.path.basename(__file__)
app_name = os.path.basename(os.path.dirname(os.getcwd()))

class ModInputWEBEX_MEETING_QUALITIES(base_mi.BaseModInput): 

    def __init__(self):
        use_single_instance = False
        super(ModInputWEBEX_MEETING_QUALITIES, self).__init__(app_name, "webex_meeting_qualities", use_single_instance) 
        self.global_checkbox_fields = None

    def get_scheme(self):
        scheme = smi.Scheme('webex_meeting_qualities')
        scheme.description = 'Webex Meeting Qualities'
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
                required_on_create=True,
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
        start_time_start = definition.parameters.get('start_time', None)
        if start_time_start is not None:
            start_time = datetime.strptime(start_time_start, "%Y-%m-%dT%H:%M:%SZ")

            if start_time <= datetime.now() - timedelta(days=7):
                raise ValueError(
                    "Start time cannot be earlier than 7 days ago. Please enter a date after {}.".format(datetime.strftime(datetime.now() - timedelta(days=7),"%Y-%m-%d")))
            pass

    def get_app_name(self):
        return "ta_cisco_webex_add_on_for_splunk"

    def collect_events(helper, ew):
        input_module.collect_events(helper, ew)

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
    exit_code = ModInputWEBEX_MEETING_QUALITIES().run(sys.argv)
    sys.exit(exit_code)