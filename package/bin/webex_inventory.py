import json
import os
import sys

from splunklib import modularinput as smi
from splunktaucclib.modinput_wrapper import base_modinput as base_mi

import input_module_webex_inventory as input_module

bin_dir = os.path.basename(__file__)
app_name = os.path.basename(os.path.dirname(os.getcwd()))


class ModInputWEBEX_INVENTORY(base_mi.BaseModInput):

    def __init__(self):
        use_single_instance = False
        super(ModInputWEBEX_INVENTORY, self).__init__(app_name, "webex_inventory", use_single_instance)
        self.global_checkbox_fields = None

    def get_scheme(self):
        scheme = smi.Scheme("webex_inventory")
        scheme.description = "Webex Inventory"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        scheme.add_argument(
            smi.Argument(
                "name",
                title="Name",
                description="Name",
                required_on_create=True,
            )
        )
        scheme.add_argument(
            smi.Argument(
                "webex_base_url",
                title="Webex Base URL",
                description="Enter the base URL for the Webex API (e.g., api.ciscospark.com, api-usgov.webex.com, api.wxcc-{region}.cisco.com).",
                required_on_create=True,
            )
        )
        scheme.add_argument(
            smi.Argument(
                "webex_endpoint",
                title="Webex API Endpoint",
                description="Enter the Webex API endpoint to query (e.g., /devices).",
                required_on_create=True,
            )
        )
        scheme.add_argument(
            smi.Argument(
                "method",
                title="HTTP Method",
                description="Select the HTTP method to use for the request (GET or POST).",
                required_on_create=True,
            )
        )
        scheme.add_argument(
            smi.Argument(
                "query_params",
                title="Query Parameters",
                description="Enter any query parameters as a JSON-formatted string (e.g., {\"param1\":\"value1\",\"param2\":\"value2\"}).",
                required_on_create=False,
            )
        )

        scheme.add_argument(
            smi.Argument(
                "request_body",
                title="Request Body",
                description="Enter the request body as a JSON-formatted string for POST requests.",
                required_on_create=False,
            )
        )
        
        scheme.add_argument(
            smi.Argument(
                "global_account",
                title="Global Account",
                description="Enter the global account name.",
                required_on_create=True,
            )
        )
        return scheme

    def validate_input(self, definition):
        del definition
        return

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
            checkbox_name_file = os.path.join(bin_dir, "global_checkbox_param.json")
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, "r") as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = []
            except Exception as e:
                self.log_error("Get exception when loading global checkbox parameter names. " + str(e))
                self.global_checkbox_fields = []
        return self.global_checkbox_fields


if __name__ == "__main__":
    exit_code = ModInputWEBEX_INVENTORY().run(sys.argv)
    sys.exit(exit_code)
