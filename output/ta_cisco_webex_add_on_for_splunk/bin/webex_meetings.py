import import_declare_test
import sys
import json

from splunklib import modularinput as smi

class WEBEX_MEETINGS(smi.Script):

    def __init__(self):
        super(WEBEX_MEETINGS, self).__init__()

    def get_scheme(self):
        scheme = smi.Scheme('webex_meetings')
        scheme.description = 'Webex Meetings'
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = True

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
                'interval',
                required_on_create=True,
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
        return

    def stream_events(self, inputs, ew):
        input_items = [{'count': len(inputs.inputs)}]
        for input_name, input_item in inputs.inputs.items():
            input_item['name'] = input_name
            input_items.append(input_item)
        event = smi.Event(
            data=json.dumps(input_items),
            sourcetype='webex_meetings',
        )
        ew.write_event(event)


if __name__ == '__main__':
    exit_code = WEBEX_MEETINGS().run(sys.argv)
    sys.exit(exit_code)