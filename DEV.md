# Develop Splunk Add-on with OAuth Support using UCC
## Create a Add-on from from scratch:
### 1. Install splunk-add-on-ucc-framework
```
pip3 install splunk-add-on-ucc-framework
```
### 2. Create `globalConfig.json` and `app.manifest`
An easy way to create desired `globalConfig.json` and `app.manifest` is by leveraging AOB. You can create a TA with desired UI components using AOB, and then use the generated `globalConfig.json` and `app.manifest` directly.

**If you use AOB, please pay attention to the following points**:
1. AOB auto-generates an `Add-on Folder Name` for your add-on, which has the format  `TA-your-add-on-name`. This format is not consistent with the built-in OAuth redirect URL format. You'd better change it to a format that only contains **lowercase** and **"_"**. 
e. g. `ta_your_add_on_name`
Two ways to change the Add-on Folder Name for AOB Add-on:
    - There is an `Edit` button right behind `Add-on Folder Name` in the AOB UI, click it to modify the Add-on Folder Name.
    - You can also manually modify it via updating `globalConfig.json` and `app. manifest`. Check the **Steps to change Add-on Folder name** section to see the details.

2. In order to get the AOB-style modular input python script, you **MUST** add `"template": "input_with_helper"` entry in each of you input. Position of this entry is 
    `globalConfig.json` > `pages` > `inputs` > `services` > next to `name`.
    ```
    "inputs": {
            "title": "Inputs",
            "description": "Manage your data inputs",
            "table": {
                "header": [
                ],
                "moreInfo": [
            },
            "services": [
                {
                    "template": "input_with_helper",
                    "name": "webex_meetings",
                    "title": "Webex Meetings",
                    ...
    ```

3. Pay attention to `"meta"` section inside `globalConfig.json`. Make sure you have `"apiVersion"` under `"meta"` 
e.g. `"apiVersion": "4.1.10".`


### 3. Create required file structure
```
mkdir <TA-name>
cd <TA-name>
cp /path/to/globalConfig.json .
mkdir package
cd package
cp /path/to/app.manifest .
touch LICENSE.txt
touch README.txt
mkdir lib
touch lib/requirements.txt
echo "splunktaucclib" > lib/requirements.txt
```

**Note**: 
1. Make sure you put `splunktaucclib` inside `lib/requirements.txt`. Otherwise the UI of the TA cannot be loaded.
2. **LICENSE.txt** and **README.txt** can be empty.


Your file structure would look like as below:
```
├── globalConfig.json
└── package
    ├── LICENSE.txt
    ├── README.txt
    ├── app.manifest
    └── lib
        └── requirements.txt
```

### 4. Run `ucc-gen` under main project directory 
```
cd <TA-name>
ucc-gen --ta-version=1.0.0
```

### 5. You will see the TA is generated under `output` folder.

### 6. Create a symbolic to $SPLUNK_APP_HOME
```
ln -s <FULL_PATH_TO_PROJECT_HOME_DIR>/output/TA-cisco-webex-add-on-for-splunk $SPLUNK_APP_HOME_DIR

e.g.
ln -s /Users/yling/practice/ucc/ucc_webex_ta/output/TA-cisco-webex-add-on-for-splunk /Applications/Splunk/etc/apps
```

### 7. Restart Splunk

---

## Add OAuth supprot to your Add-on
UCC framework has out of box support for OAuth. Here are the steps on how you can add OAuth support to your Add-on's global Account section.

### 1. Add `oauth` type entity under `globalConfig.json` > `"pages"` > `"configuration"`
```
 "configuration": {
            "title": "Configuration",
            "description": "Set up your add-on",
            "tabs": [
                {
                    "name": "account",
                    "title": "Account",
                    "table": {
                        "header": [
                            {
                                "field": "name",
                                "label": "Account name"
                            },
                            {
                                "label": "Authentication Type",
                                "field": "auth_type"
                            }
                        ],
                        "actions": [
                            "edit",
                            "delete",
                            "clone"
                        ]
                    },
                    "entity": [
                        {
                            "field": "name",
                            "label": "Account name",
                            "type": "text",
                            "required": true,
                            "help": "Enter a unique name for this account.",
                            "validators": [
                                {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 50,
                                    "errorMsg": "Length of Account name should be between 1 and 50"
                                },
                                {
                                    "type": "regex",
                                    "pattern": "^[a-zA-Z]\\w*$",
                                    "errorMsg": "Account name must start with a letter and followed by alphabetic letters, digits or underscores."
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "label": "Endpoint",
                            "field": "endpoint",
                            "help": "Enter Endpoint",
                            "options": {
                                "display": false
                            },
                            "defaultValue": "webexapis.com"
                        },
                        {
                            "field": "oauth",
                            "label": "Not used",
                            "type": "oauth",
                            "options": {
                                "auth_type": [
                                    "basic",
                                    "oauth"
                                ],
                                "basic": [
                                    {
                                        "oauth_field": "username",
                                        "label": "User Name",
                                        "field": "username",
                                        "help": "Enter Account name."
                                    },
                                    {
                                        "oauth_field": "password",
                                        "label": "Password",
                                        "field": "password",
                                        "encrypted": true,
                                        "help": "Enter Password."
                                    }
                                ],
                                "oauth": [
                                    {
                                        "oauth_field": "client_id",
                                        "label": "Client Id",
                                        "field": "client_id",
                                        "help": "Enter Client Id."
                                    },
                                    {
                                        "oauth_field": "client_secret",
                                        "label": "Client Secret",
                                        "field": "client_secret",
                                        "encrypted": true,
                                        "help": "Enter Client Secret."
                                    },
                                    {
                                        "oauth_field": "redirect_url",
                                        "label": "Redirect url",
                                        "field": "redirect_url",
                                        "help": "Please add this redirect URL in your app."
                                    }
                                ],
                                "auth_label": "Auth Type",
                                "oauth_popup_width": 600,
                                "oauth_popup_height": 600,
                                "oauth_timeout": 180,
                                "auth_code_endpoint": "/v1/authorize",
                                "access_token_endpoint": "/v1/access_token"
                            }
                        }
                    ],
                    "hook": {
                        "src": "account_hook",
                        "type": "external"
                    }
                },
                ...
            ]
},
    ...
```

Below is the explanation of each entry under `"entity"`:
- `Account name`: Input Text box for Unique Account Name
- `Endpoint`: Input Text box for base endpoint for which we want to build oauth support. For example, for Webex the oauth flow will be built on `https://webexapis.com/v1/authorize` and `https://webexapis.com/v1/access_token`. The base endpint is `webexapis.com` here.

    **Note**: Typically, the base endpoint is static. Therefore, instead of asking user to enter it, we can 
    1. set a defualt value for it 
        `"defaultValue": "webexapis.com"`
    2. and then hide it from UI. 
        `"options": {"display": false}`
- `oauth`: Oauth type enity
    This is the most important entry that you need to add for Oauth support. (**Note**: `type` field value must be **`oauth`** in this entry).
    You can find detailed explanation of each field [here](https://splunk.atlassian.net/wiki/spaces/PROD/pages/314016308892/UCC+5.X+Development+Guide#7.10.-OAuth-support-for-UCC). Check the Add-on related product's API to identify which fileds are needed for your Add-on.

    **The following are the essential fields that you MUST-HAVE:**
    - `client_id` this is client id for the your app for which you want auth.
    
    - `client_secret` this is client secret for the your app for which you want auth.
    
    - `redirect_url` this will show redirect url which needs to be put in app's redirect url.
    
    - `auth_code_endpoint` this must be present and its value should be endpoint value for getting the auth_code using the app. For example, for Webex the url to get auth_code is `https://webexapis.com/v1/authorize` then this will have value `/v1/authorize`.
    
    - `access_token_endpoint` this must be present and its value should be endpoint value for getting access_token using the auth_code received. For example, for Webex the url to get access token is `https://webexapis.com/v1/access_token` then this will have value `/v1/access_token`.

### 2. Add `Scopes` by leveraging custom hook (Optional)
In most cases, you need to specify the permission scopes for your App, and you also need to include these scopes in the Authorization flow. Currently, the UCC framework doesn't have a built-in field for supporting adding scopes. You need to leverage a custom hook to tweak this. (**Note**: If your app doesn't need `scope` you can skip this step).

1. Add the custom hook, which is a javescript file (e.g. `account_hook.js`) , under `/package/appserver/static/js/build/custom/account_hook.js`. 
    You can find Custom Hook example with explaination [here](https://splunk.atlassian.net/wiki/spaces/PROD/pages/314016308892/UCC+5.X+Development+Guide#7.4.1.1.1.-Custom-Hook-Example).

    In the following example, we add a custom hook, `account_hook.js`, to manually append the `scopes` and `state` at the end of redirect_url. So that when user clicks the `Save` button, it will send a GET request to the correct URL with the `scope` and `state` strings.
    
    ```
    // account_hook.js
    class AccountHook {
        /**
         * Form hook
         * @constructor
         * @param {Object} globalConfig - Global configuration.
         * @param {string} serviceName - Service name
         * @param {object} state - Initial state of the form
         * @param {string} mode - Form mode. Can be edit, create or clone
         * @param {object} util - Object containing utility methods
         *                        {
         *                          setState,
         *                          setErrorMsg,
         *                          setErrorFieldMsg,
         *                          clearAllErrorMsg
         *                        }
         */
        constructor (globalConfig, serviceName, state, mode, util) {
            this.globalConfig = globalConfig
            this.serviceName = serviceName
            this.state = state
            this.mode = mode
            this.util = util
        }
      
        /*
          Put logic here to execute javascript on Create UI.
        */
        onCreate () {}
      
        /*
          Put logic here to execute javascript when UI gets rendered.
        */
        onRender () {}
        /*
          Put form validation logic here.
          Return ture if validation pass, false otherwise.
          Call displayErrorMsg when validtion failed.
        */
        onSave (dataDict) {
            console.log("[-] onSave...")
            console.log("[-] dataDict: ", dataDict);
            const accountName = dataDict.name
            const authType = dataDict.auth_type
            let endpoint = dataDict.endpoint
            console.log("[-] ", accountName, authType, endpoint)
            if (authType === 'oauth') {
                // hard code the scope and state
                const scopeString = "&scope=spark:kms meeting:schedules_read meeting:participants_read&state=set_state_here"
                // append scope string at the end of redirect url
                // to make it send the correct GET request to Webex server with required scopes and state
                const redirect_url = dataDict.redirect_url.concat(scopeString)
                this.util.setState((prevState) => {
                    const data = { ...prevState.data }
                    data.redirect_url.value = redirect_url
                    return { data }
                })
            }
            return true
        }
      
        /*
          Put logic here to execute javascript to be called after save success.
        */
        onSaveSuccess () {}
        /*
          Put logic here to execute javascript to be called on save failed.
        */
        onSaveFail () {}
        /*
          Put logic here to execute javascript after loading edit UI.
        */
        onEditLoad () {}
      }
      
      export default AccountHook
    ``` 
2. Specify your custom hook in the `globalConfig.json`. Position of this tag is next to the entity tag.

    ```
    "hook": {
      "src": "account_hook",
      "type": "external"
    }
    ```
    Here, the value of `"src"` is your javascript file's name without extension.

### 3. Add custom REST handler
By taking advantage of built-in OAuth support we will have the required custom endpoint and corresponding custom REST handler auto-setup. What we only should do is modify the custom REST handler python script as needed. 

Once you complete the above steps you can run `ucc-gen`. You will see

- `restmap.conf` with a custom endpoint for OAuth is auto-generated.

    ```
    [admin_external:ta_cisco_webex_add_on_for_splunk_oauth]
    handlertype = python
    python.version = python3
    handlerfile = ta_cisco_webex_add_on_for_splunk_rh_oauth.py
    handleractions = edit
    handlerpersistentmode = true
    ```


- `web.conf` with a custom endpoint for OAuth is auto-generated.

    ```
    [expose:ta_cisco_webex_add_on_for_splunk_oauth]
    pattern = ta_cisco_webex_add_on_for_splunk_oauth
    methods = POST, GET
    
    [expose:ta_cisco_webex_add_on_for_splunk_oauth_specified]
    pattern = ta_cisco_webex_add_on_for_splunk_oauth/*
    methods = POST, GET, DELETE
    ```


- `Custom REST handler python script` is auto-generated under `/output/<YOUR-TA-NAME>/bin/<YOUR-TA-NAME>_rh_oauth.py`. It's a well-defined template, and you can modify it as needed. Typically, you don't need to modify it too much.
In the Webex example, since we modified the `redirect_uri`  by adding  `scopes` and `state` in the `account_hook.js`. We need to correct it here so that it uses the correct `redirect_uri` to exchange the access token when it sends a POST request to the Webex server.

    ```
    # /output/ta_cisco_webex_add_on_for_splunk/bin/ta_cisco_webex_add_on_for_splunk_rh_oauth.py
    
    import import_declare_test
    """
    This module will be used to get oauth token from auth code
    """
    
    import urllib
    try:
        from urllib import urlencode
    except:
        from urllib.parse import urlencode
    from httplib2 import Http, ProxyInfo, socks
    import splunk.admin as admin
    from solnlib import log
    from solnlib import conf_manager
    from solnlib.utils import is_true
    import json
    
    log.Logs.set_context()
    logger = log.Logs().get_logger('ta_cisco_webex_add_on_for_splunk_rh_oauth2_token')
    
    # Map for available proxy type
    
    # Note: Comment L40 to get rid of the following error
    # Python ERROR: AttributeError: module 'socks' has no attribute 'PROXY_TYPE_HTTP_NO_TUNNEL'
    # UI ERROR: 500 Internal Server Error
    _PROXY_TYPE_MAP = {
        'http': socks.PROXY_TYPE_HTTP,
        # 'http_no_tunnel': socks.PROXY_TYPE_HTTP_NO_TUNNEL,
        'socks4': socks.PROXY_TYPE_SOCKS4,
        'socks5': socks.PROXY_TYPE_SOCKS5,
    }
    
    """
    REST Endpoint of getting token by OAuth2 in Splunk Add-on UI Framework.
    """
    
    
    class ta_cisco_webex_add_on_for_splunk_rh_oauth2_token(admin.MConfigHandler):
    
        """
        This method checks which action is getting called and what parameters are required for the request.
        """
    
        def setup(self):
            if self.requestedAction == admin.ACTION_EDIT:
                # Add required args in supported args
                for arg in (
                    'url', 
                    'method',
                    'grant_type',
                    'code',
                    'client_id',
                    'client_secret',
                    'redirect_uri'
                ):
                    self.supportedArgs.addReqArg(arg)
            return
    
        """
        This handler is to get access token from the auth code received
        It takes 'url', 'method', 'grant_type', 'code', 'client_id', 'client_secret', 'redirect_uri' as caller args and
        Returns the confInfo dict object in response.
        """
    
        def handleEdit(self, confInfo):
    
            try:
                logger.debug("In OAuth rest handler to get access token")
                # Get args parameters from the request
    
                url = self.callerArgs.data['url'][0]
                logger.debug("oAUth url %s", url)
                proxy_info = self.getProxyDetails()
    
                http = Http(proxy_info=proxy_info)
                method = self.callerArgs.data['method'][0]
    
                # remove the scope string from redirect_uri
                redirect_uri = self.callerArgs.data['redirect_uri'][0].split("&")[0]
                # Create payload from the arguments received
                payload = {
                    'grant_type': self.callerArgs.data['grant_type'][0],
                    'code': self.callerArgs.data['code'][0],
                    'client_id': self.callerArgs.data['client_id'][0],
                    'client_secret': self.callerArgs.data['client_secret'][0],
                    'redirect_uri': redirect_uri,
                }
                headers = {"Content-Type": "application/x-www-form-urlencoded", }
                # Send http request to get the accesstoken
                resp, content = http.request(url,
                                                method=method,
                                                headers=headers,
                                                body=urlencode(payload))
                content = json.loads(content)
                # Check for any errors in response. If no error then add the content values in confInfo
                if resp.status == 200:
                    for key, val in content.items():
                        confInfo['token'][key] = val
                else:
                    # Else add the error message in the confinfo
                    confInfo['token']['error'] = content['error_description']
                logger.info(
                    "Exiting OAuth rest handler after getting access token with response %s", resp.status)
            except Exception as exc:
                logger.exception(
                    "Error occurred while getting accesstoken using auth code")
                raise exc()
    
        """
        This method is to get proxy details stored in settings conf file
        """
    
        def getProxyDetails(self):
            # Create confmanger object for the app with realm
            cfm = conf_manager.ConfManager(self.getSessionKey(
            ), "ta_cisco_webex_add_on_for_splunk", realm="__REST_CREDENTIAL__#ta_cisco_webex_add_on_for_splunk#configs/conf-ta_cisco_webex_add_on_for_splunk_settings")
            # Get Conf object of apps settings
            conf = cfm.get_conf('ta_cisco_webex_add_on_for_splunk_settings')
            # Get proxy stanza from the settings
            proxy_config = conf.get("proxy", True)
            if not proxy_config or not is_true(proxy_config.get('proxy_enabled')):
                logger.info('Proxy is not enabled')
                return None
    
            url = proxy_config.get('proxy_url')
            port = proxy_config.get('proxy_port')
    
            if url or port:
                if not url:
                    raise ValueError('Proxy "url" must not be empty')
                if not self.is_valid_port(port):
                    raise ValueError(
                        'Proxy "port" must be in range [1,65535]: %s' % port
                    )
    
            user = proxy_config.get('proxy_username')
            password = proxy_config.get('proxy_password')
    
            if not all((user, password)):
                logger.info('Proxy has no credentials found')
                user, password = None, None
    
            proxy_type = proxy_config.get('proxy_type')
            proxy_type = proxy_type.lower() if proxy_type else 'http'
    
            if proxy_type in _PROXY_TYPE_MAP:
                ptv = _PROXY_TYPE_MAP[proxy_type]
            elif proxy_type in _PROXY_TYPE_MAP.values():
                ptv = proxy_type
            else:
                ptv = socks.PROXY_TYPE_HTTP
                logger.info('Proxy type not found, set to "HTTP"')
    
            rdns = is_true(proxy_config.get('proxy_rdns'))
    
            proxy_info = ProxyInfo(
                proxy_host=url,
                proxy_port=int(port),
                proxy_type=ptv,
                proxy_user=user,
                proxy_pass=password,
                proxy_rdns=rdns
            )
            return proxy_info
    
        """
        Method to check if the given port is valid or not
        :param port: port number to be validated
        :type port: ``int``
        """
    
        def is_valid_port(self, port):
            try:
                return 0 < int(port) <= 65535
            except ValueError:
                return False
    
    if __name__ == "__main__":
        admin.init(ta_cisco_webex_add_on_for_splunk_rh_oauth2_token, admin.CONTEXT_APP_AND_USER)
    
    ```


---

## Findings
1. In contrast on AOB, ucc-gen will not auto-generate sourcetype for either input or log files If you define soucetype for your input in AOB, feel free to copy `input.conf` and `props.conf` to `./package/default/inputs.conf` and `./package/default/props.conf`.

Re-run `ucc-gen` the desired `input.conf` and `props.conf` will be copied into your TA.

## Steps to change Add-on Folder name
1. globalConfig.json > meta > name
```
"meta": {
        "name": "ta_cisco_webex_add_on_for_splunk",
        "displayName": "Cisco Webex Add on for Splunk",
        "version": "1.0.0",
        "restRoot": "ta_cisco_webex_add_on_for_splunk",
        "apiVersion": "4.1.10",
        "schemaVersion": "0.0.3"
    }
```

2. app.manifest > info > id > name
```
"info": {
    "title": "Cisco Webex Add on for Splunk",
    "id": {
      "group": null,
      "name": "ta_cisco_webex_add_on_for_splunk",
      "version": "1.0.0"
    }
```


## Troubleshooting
### ERROR: Config is not valid. Error: 'apiVersion' is a required property
- Make sure you have `"apiVersion": "3.2.0"` under `meta` section in `globalConfig.json`

### ModuleNotFoundError: No module named 'mmap'
- If you encounter this error after running `ucc-gen`, please try to setup a new python3 (>=v3.7) virtual environment and re-run `ucc-gen`

### 404 Not found for redirect URL
```
Request URL: http://localhost:8000/en-US/splunkd/__raw/servicesNS/nobody/TA-cisco-webex-add-on-for-splunk/TA-cisco-webex-add-on-for-splunk_oauth/oauth?output_mode=json
Request Method: POST
Status Code: 404 Not Found
```

- verify the oauth endpoint in `restmap.conf` and `web.conf`

```
http://localhost:8000/en-US/splunkd/__raw/servicesNS/nobody/<TA_NAME>/<OAUTH_ENDPOINT>/oauth?output_mode=json
```
- make sure the oauth endpoint is consistent.