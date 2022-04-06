# Steps:
1. Install splunk-add-on-ucc-framework
```
pip3 install splunk-add-on-ucc-framework
```
2. Create `globalConfig.json` and `app.manifest`
Leverage AOB to create a TA with desired UI components, then we can use the built-in `globalConfig.json` and `app.manifest` directly.
**Note**: Pay attention to `"meta"` section inside `globalConfig.json`. Make sure you have `"apiVersion": "3.2.0"` under `"meta"`.

3. Create required file structure
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
echo "splunktaucclib" > lib/test
```

**Note**: Make sure you put `splunktaucclib` inside `lib/requirements.txt`. Otherwise the UI of the TA cannot be loaded.


You file structure would look like as below:
```
├── globalConfig.json
└── package
    ├── LICENSE.txt
    ├── README.txt
    ├── app.manifest
    └── lib
        └── requirements.txt
```

4. Run `ucc-gen` under main project directory 
```
cd <TA-name>
ucc-gen --ta-version=1.0.0
```

5. You will see the TA was generated under `output` folder.

6. Create a symbolic to $SPLUNK_APP_HOME
```
ln -s <FULL_PATH_TO_PROJECT_HOME_DIR>/output/TA-cisco-webex-add-on-for-splunk $SPLUNK_APP_HOME_DIR

e.g.
ln -s /Users/yling/practice/ucc/ucc_webex_ta/output/TA-cisco-webex-add-on-for-splunk /Applications/Splunk/etc/apps
```

7. Restart Splunk


# Findings
1. In contrast on AOB, ucc-gen will not auto-generate sourcetype for either input or log files If you define soucetype for your input in AOB, feel free to copy `input.conf` and `props.conf` to `./package/default/inputs.conf` and `./package/default/props.conf`.

Re-run `ucc-gen` the desired `input.conf` and `props.conf` will be copied into your TA.


# Troubleshooting
### ERROR: Config is not valid. Error: 'apiVersion' is a required property
- Make sure you have `"apiVersion": "3.2.0"` under `meta` section in `globalConfig.json`