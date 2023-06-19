# Cisco Webex Add-on for Splunk
> **Cisco Webex Add-on for Splunk** is an Add-on to pull in data from _[Webex REST API](https://developer.webex.com/docs/basics)_ to Splunk.

Here are the endpoints and their mapping soucetypes.
| Splunk Input       | Webex Endpoint        | Splunk Sourcetype               |
|--------------------|-----------------------|---------------------------------|
| Webex Meetings       | [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         |
| Webex Meetings       | [Meeting Participants](https://developer.webex.com/docs/api/v1/meeting-participants/list-meeting-participants)                       | cisco:webex:meetings:participants             |
| Webex Meetings Summary Report       | [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports)                       | cisco:webex:meeting:usage:reports         |
| Webex Meetings Summary Report       | [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports)                       | cisco:webex:meeting:attendee:reports             |
| Webex Admin Audit Events       | [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events)                               | cisco:webex:admin:audit:events               |

## Getting Started
### Installation Instructions

#### Installation Steps for `Splunk Enterprise`
- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall) to install the Add-on in a single-instance Splunk Enterprise deployment.

- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall) to install the Add-on in a distributed Splunk Enterprise deployment.

#### Installation Steps for `Splunk Cloud`
Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/SplunkCloudinstall) to install the Add-on in Splunk Cloud.

### Create a Webex Integration
The Cisco Webex Add-on for Splunk supports OAuth2 Authentication, which allows third-party integrations to get a temporary access token for authenticating API calls. Therefore, creating an **Admin-level Webex integration** is required to work along with this Add-on.

**Note**: The [Meeting Participants](https://developer.webex.com/docs/api/v1/meeting-participants/list-meeting-participants) endpoint requires the `spark-compliance:meetings_read` scope. If you need to use **Webex Meetings** Input, the Webex account need to have the **Compliance Officer role** assigned.

**Only the Webex Meetings Input needs the Compliance Officer role. The other two Inputs don’t require your account to have this role.**

Please follow the following steps to create a dedicated Webex integration for this Add-on. Further documentation can be found [here](https://developer.webex.com/docs/integrations).

1. **Registering your Integration**:
    - Visit the [Webex for Developers](https://developer.webex.com/) and then log in using your **Webex Admin Account**
    - Select `My Webex Apps` from the menu under your avatar at the top of this page
    - Click `Create a New App` then `Create an Integration` to start the wizard
2. **Provide app related information**:
    - **Integration name**: Enter a name for yor integration. `e.g. Webex Integration for Splunk`
    - **Icon**: Upload your own or select from the defaults
    - **Description**: Provide some details about your integration
    - **Redirect URI(s)**: Follow the following steps to retrieve your Redirect URI:
        - Open **Cisco Webex Add-on for Splunk** in Splunk. Go to `Configuration > Account > Add`. The Redirect URI will show up in the `Redirect url` field. Please copy and paste it to the `Redirect URI(s)` field in the Webex Integration.
        - **For Splunk Heavy Forwarders (or IDM)**: please replace the `{domain}` with the domain of your Splunk Heavy Forwarder (or IDM). For example, if the domain of your HF or IDM is `example.splunk.link`, then the Redirect URI you have to enter is:  `https://example.splunk.link/en-US/app/ta_cisco_webex_add_on_for_splunk/ta_cisco_webex_add_on_for_splunk_redirect`
    
    - **Scopes**: Please select the following scopes:
    **Note**: No matter whether you will use Webex Meetings Input or not, you **MUST** select all the following scopes.
        - `meeting:admin_schedule_read`
        - `meeting:admin_participants_read`
        - `spark-compliance:meetings_read`
        - `spark:organizations_read`
        - `audit:events_read`
        - `meeting:admin_config_read`

3. Click **Add Integration** on the bottom of the page, your `Client ID` and `Client Secret` are ready to use.

### Configuration Instructions
Open the Web UI for the Heavy Forwarder (or IDM). Access the Add-on from the list of applications. Please follow the following steps in order:

#### 1. Create Account
- Click on the `Configuration` button on the top left corner.
- Click on the `Account` button.
- Click on the `Add` button on the top right to create a new account.
-  Enter the following details in the pop-up box:
    - **Account name**: Enter a unique name for this account.
    - **Webex API Base Endpoint**: Enter your Webex API Base Endpoint. The default one is `webexapis.com`.
    - **Client ID**: Enter the `Client ID` that you obtained above here.
    - **Client Secret**: Enter the `Client Secret` that you obtained above here.
    - **Redirect URI**: The Redirect URI will auto show up. 
    - Click on the `Add` button.


#### 2. Create Input

**Webex Meetings Input**

The **Webex Meetings** input is used to fetch the data from both [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings) endpoint and [Meeting Participants](https://developer.webex.com/docs/api/v1/meeting-participants/list-meeting-participants) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting participants.

**Please Note**: The input only returns the **historical** meeting reports and participant reports. The reports are only ingested into Splunk after the meetings have ended. To avoid ingesting incomplete data, the input will have a 12 hours delay.

The `Start Time` is required. Set the starting date and time to fetch meetings & participants. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). Start Time **MUST** be prior to 12 hours before current time.

The `End Time` is optional. If you set it to be a specific date, only reports within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one second) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. Start Time must be prior to 12 hours before current time.
    - **End Time** (_optional_): End date and time in the format YYYY-Mon-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. End Time must be after the Start Time.
- Click on the `Add` green button on the bottom right of the pop up box.

**Webex Meetings Summary Report Input**

The **Webex Meetings Summary Report** input is used to fetch the data from both [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports) endpoint and [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting attendees.

**Please Note**: The input only returns the **historical** meeting reports and attendee reports, since these two endpoints only contain historical data. The input will have a few hours delay due to the API behavior. Typically, meeting data is not showing up in the API until 2 to 3 hours after the meetings end. Therefore, the meetings data is only ingested 2 to 3 hours after the meetings end.

The `Start Time` is required. Set the starting date and time to fetch meetings & attendees. The Start Time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.

The `End Time` is optional. If you set it to be a specific date, only reports within the time range from Start Time to End Time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). The interval between Start Time and End Time cannot exceed 30 days. Leave it blank if an ongoing ingestion mode is needed.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one second) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Site Name** (_required_): Site Name of the Webex Meeting account. `example: example.webex.com`
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.
    - **End Time** (_optional_): End date and time in the format YYYY-Mon-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The interval between Start Time and End Time cannot exceed 30 days.
- Click on the `Add` green button on the bottom right of the pop up box.

**Webex Admin Audit Events Input**

The **Webex Admin Audit Events** input is used to fetch the data from [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events) endpoint. It allows users to retrieve organization-wide audit logs all over the account.

The `Start Time` is required. Set the starting date and time to fetch admin audit events. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-01-01T00:00:00.000Z). If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.

The `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-02-01T00:00:00.000Z).

**Please Note**: Due to the API behavior, the selected time range cannot be more than a year. Therefore, If you want to obtain the audit logs that happened more than one year ago, you **MUST** fill in both `Start Time` and `End Time`, and ensure that the range does not exceed one year.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SS.SSSZ, `example:2023-01-01T00:00:00.000Z`. If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SS.SSSZ.(Optional), `example:2023-02-01T00:00:00.000Z`. End Time must be after the Start Time.
- Click on the `Add` green button on the bottom right of the pop up box.

## Versions Supported

  - Tested for installation and basic ingestion on Splunk 9.X and 8.2 for **CentOS** system.

> Built by Splunk's FDSE Team (#team-fdse).

## Reference 
- This Add-on was built via splunk-add-on-ucc-framework

## Credits & Acknowledgements
* Yuan Ling
* Marie Duran