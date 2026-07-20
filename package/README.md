# Cisco Webex Add-on for Splunk
> **Cisco Webex Add-on for Splunk** is an Add-on to pull in data from _[Webex REST API](https://developer.webex.com/docs/basics)_ to Splunk.

#### Here are the endpoints, their corresponding source types, and the required scopes.
| Splunk Input       | Webex Endpoint        | Splunk Sourcetype               | Required Scopes                 |
|--------------------|-----------------------|---------------------------------|---------------------------------|
| Webex Generic Endpoint                | [Webex API](https://developer.webex.com/messaging/docs/basics)                       | cisco:webex:<**API Endpoint**>       | Refer to the endpoint documentation to confirm the required scopes |
| Webex Inventory       | [Any Webex API Endpoint](https://developer.webex.com/docs/basics)                       | User-defined (e.g., cisco:webex:inventory:devices)         | Refer to the endpoint documentation to confirm the required scopes |
| Webex Scheduled Meetings       | [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         | meeting:admin_schedule_read spark-admin:people_read   |
| Webex Meetings Summary Report       | [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports)                       | cisco:webex:meeting:usage:reports         | meeting:admin_schedule_read meeting:admin_participants_read meeting:admin_config_read    |
| Webex Meetings Summary Report       | [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports)                       | cisco:webex:meeting:attendee:reports             | meeting:admin_schedule_read meeting:admin_participants_read meeting:admin_config_read  |
| Webex Admin Audit Events       | [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events)                               | cisco:webex:admin:audit:events              | audit:events_read spark:organizations_read  |
| Webex Meeting Qualities       | [Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities)                               | cisco:webex:meeting:qualities              | analytics:read_all   |
| Webex Detailed Call History       | [Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history)                               | cisco:webex:call:detailed_history             | spark-admin:calling_cdr_read |
| Webex Security Audit Events       | [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events)                               | cisco:webex:security:audit:events            | audit:events_read spark:organizations_read |
| Webex Contact Center - Search       | [Webex Contact Center - Search](https://developer.webex.com/webex-contact-center/docs/api/v1/search/search)                               | cjp:config or cjp:config_read            | cisco:webex:contact:center:AAR cisco:webex:contact:center:ASR cisco:webex:contact:center:CAR cisco:webex:contact:center:CSR |

## Getting Started
### Installation Instructions

#### Installation Steps for `Splunk Enterprise`
- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall) to install the Add-on in a single-instance Splunk Enterprise deployment.

- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall) to install the Add-on in a distributed Splunk Enterprise deployment.

#### Installation Steps for `Splunk Cloud`
Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/SplunkCloudinstall) to install the Add-on in Splunk Cloud.

### Create a Webex Integration
The Cisco Webex Add-on for Splunk supports OAuth2 Authentication, which allows third-party integrations to get a temporary access token for authenticating API calls. Therefore, creating an **Admin-level Webex integration** is required to work along with this Add-on.
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
    
    - **Scopes**: Please select only the scopes you need.
    **Note**: Refer to the table above to identify which scopes are required for the inputs you are interested in.

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
    - **Scopes**: Select the authorization scopes. Please ensure that the scopes entered here match those selected in your Webex Integration.
    - Click on the `Add` button.


#### 2. Create Input

**Webex Generic Endpoint**

The **Webex Generic Endpoint** provides the flexibility to create a custom input using the Webex API endpoint of your choice. If you encounter scenarios where the predefined input options do not meet your requirements, you can use this option to enable data ingestion from a different source.

Keep in mind that the endpoint you want to use may require special permissions, roles, and/or scopes. Please refer to the API documentation to see the requirements needed to enable data ingestion for the endpoint.

Enter a `Start Time` whenever it is supported by the endpoint to help avoid duplicates. If an `End Time` is specified, data will be fetched up to that time; otherwise, data will be fetched up to the current time. If a `Start` or `Created` time is present in the response, it will be saved as a checkpoint and used as the `Start Time` for the next run.

Some endpoints require specific query parameters to function correctly. Users can add these parameters using the `Query Params` field. The input also supports path parameters in the URL, which should be included in the `API Endpoint` field.

Most endpoints require a **GET** request. If a **POST** request is necessary, select `POST` from the `Request Method` dropdown. You may also provide the payload in the `Request Body` field if required.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **API Endpoint(_required_)**: The Webex API endpoint. It is not necessary to include a leading slash as for example: `device`, or `devices/12345678`.
    - **Webex Base API URL(_required_)**: SEnter the base URL for the endpoint. Most Webex APIs use `webexapis.com`, but some may require a different base URL. For example, endpoints that require the `analytics:read_all` scope often use `analytics.webexapis.com`. Always refer to the endpoint documentation to confirm the correct base URL.
    - **Start Time**(_required_): Inclusive start date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, e.g. `2023-01-01T00:00:00Z`.  Be aware of the endpoint limitations and valid ranges.
    - **End Time**(_optional_): End date and time in the format `YYYY-Mon-DDTHH:MM:SSZ`, e.g. `2023-02-01T00:00:00Z`. Leave blank if an ongoing ingestion mode is needed. Be aware of the endpoint limitations and valid ranges.
    - **Request Method**(_required_): Select the Request Method.
    - **Query Params**(_optional_): Include any query parameters for the endpoint. For multiple parameters, enter them as comma-separated values (e.g. `locationId=0000000, messageId=0000000, teamId=0000000`).
    - **Request Body**(_optional_): Please enter it as a JSON-formatted string. Example: {"query":"query { devices(type: CONTROLLER) { hostName ipAddress version } }","variables":{"startTime":1672531200000,"endTime":1675209600000}}
- Click on the `Add` green button on the bottom right of the pop-up box.


**Webex Inventory Input**

The **Webex Inventory** input allows you to query any Webex API endpoint on a fixed interval and index the response as events. This input is designed for inventory-style endpoints that return a collection of resources (e.g., devices, locations, workspaces, people).

Unlike the Generic Endpoint input, Webex Inventory does not maintain state between runs - it re-indexes the full response from the API endpoint on each interval. This makes it ideal for tracking complete collections of resources that don't change frequently. Each run is tagged with a unique, sortable batch_id (epoch timestamp) for easy correlation of events from the same collection run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **API Endpoint** (_required_): The Webex API endpoint to query (e.g., `devices`, `workspaces`, `locations`). Do not include a leading slash.
    - **Webex Base API URL** (_required_): Enter the base URL for the endpoint. Usually `webexapis.com`, but some endpoints may require different base URLs (e.g., `analytics.webexapis.com` for analytics-related endpoints). Default: `webexapis.com`.
    - **Request Method** (_required_): Select `GET` (default) or `POST`. Most endpoints use GET.
    - **Query Params** (_optional_): Include any query parameters for the endpoint as comma-separated values (e.g., `max=500, type=RoomDevice`).
    - **Request Body** (_optional_): For POST requests, enter the payload as a JSON-formatted string.
    - **Sourcetype** (_required_): Enter a sourcetype name for identifying the data in Splunk (e.g., `cisco:webex:inventory:devices`).
- Click on the `Add` green button on the bottom right of the pop-up box.


**Webex Scheduled Meetings Input**

The **Webex Scheduled Meetings** input is used to fetch the active scheduled meetings from [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings) endpoint. It allows users to retrieve account-wide scheduled meetings of all users in your organization.

Query parameters used for this input:
- `meetingType: scheduledMeeting`
- `hostEmail: <HOST_EMAIL>`, where all HOST_EMAILs are getting from [List People](https://developer.webex.com/docs/api/v1/people/list-people) endpoint

**Note: In order to avoid ingesting duplicate meetings, each scheduled meeting will be only ingested when it reaches its start time. It doesn’t pull in the future scheduled meetings whose start time is in the future.**

The `Interval` is required. It's used to specify how often it hits the Webex Meetings endpoint to pull the scheduled meetings in. The ingestion time increase as the number of users increases. If you have more than 100 users in your organization, it's recommended to set the interval to be at least 300 (5 mins).

The `Start Time` is required. Set the starting date and time to fetch the scheduled meetings. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). This input aims to get active scheduled meetings, it's recommended to set Start Time to the current time. For example, the current time is `2023-08-01T10:05:28Z`, you can set it as `2023-08-01T00:00:00Z`. If you'd like to get all historical meetings, please use the **Webex Meetings Summary Report Input**.

The `End Time` is optional. If you set it to be a specific date, only the scheduled meetings within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the end time of the last round as the checkpoint, and will be used as the `Start Time` (advancing by one second) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ. It's recommended to set Start Time to the current time. For example, the current time is `2023-08-01T10:05:28Z`, you can set it as `2023-08-01T00:00:00Z`.
    - **End Time** (_optional_): End date and time in the format YYYY-Mon-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. End Time must be after the Start Time.
- Click on the `Add` green button on the bottom right of the pop-up box.

**Webex Meetings Summary Report Input**

The **Webex Meetings Summary Report** input is used to fetch the data from both [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports) endpoint and [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting attendees.

**Please Note**: The input only returns the **historical** meeting reports and attendee reports, since these two endpoints only contain historical data. The input includes a 24‑hour delay due to the behavior of the API. According to the Webex documentation, “The report data for a meeting should be available within 24 hours after the meeting ends.” To ensure the data is complete and to avoid data gaps, the input ingests meeting data only after a full 24 hours have passed since the meeting ended.

The `Start Time` is required. Set the starting date and time to fetch meetings & attendees. The Start Time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). The start time must be set to 24 hours prior to the current UTC time. The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.

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
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The start time must be set to 24 hours prior to the current UTC time. The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.
    - **End Time** (_optional_): End date and time in the format YYYY-Mon-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The interval between Start Time and End Time cannot exceed 30 days.
- Click on the `Add` green button on the bottom right of the pop-up box.

**Webex Admin Audit Events Input**

The **Webex Admin Audit Events** input is used to fetch the data from [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events) endpoint. It allows users to retrieve organization-wide audit logs all over the account.

The `Start Time` is required. Set the starting date and time to fetch admin audit events. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.

The `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).

**Please Note**: Due to the API behavior, the selected time range cannot be more than a year. Therefore, If you want to obtain the audit logs that happened more than one year ago, you **MUST** fill in both `Start Time` and `End Time`, and ensure that the range does not exceed one year.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. End Time must be after the Start Time.
- Click on the `Add` green button on the bottom right of the pop-up box.

**Webex Meeting Qualities**

The **Webex Meeting Qualities** input is used to fetch the data from [Webex Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities) endpoint. It allows users to retrieve quality data for meetings. Only organization administrators can retrieve meeting quality data.

The `Start Time` is required. Set the starting date and time to fetch meeting quality data. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). Due to the Webex API limitation, Quality information may be retrieved for up to 7 days. The Start Time **MUST** be within 7 days from the current time.

The `End Time` is optional. If you set it to be a specific date, only data within the time range from Start time to End time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). Leave it blank if an ongoing ingestion mode is needed.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The Start Time **MUST** be within 7 days from the current time.
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed.
- Click on the `Add` green button on the bottom right of the pop-up box.


**Webex Detailed Call History**

The **Webex Detailed Call History** input is used to fetch the data from [Webex Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history) endpoint. It allows users to retrieve detailed data from calls. Only organization administrators can retrieve the data and it requires the administrator role "Webex Calling Detailed Call History API access" to be enabled.

The `Start Time` is required. Set the starting date and time to fetch the calls data. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). The Start Time **MUST** must be between 5 minutes ago and 48 hours ago, more than that is not possible.

The `End Time` is optional. If you set it to be a specific date, only data within the time range from Start time to End time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). Leave it blank if an ongoing ingestion mode is needed. The End Time **MUST** be later than the Start Time but no later than 48 hours.

The `Locations` field is also optional. You can include up to 10 comma-separed locations, and each location name should the same as shown in the Control Hub.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest call start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The Start Time **MUST** must be between 5 minutes ago and 48 hours ago.
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The End Time **MUST** be later than the Start Time but no later than 48 hours.
    - **Locations** (_optional_): Enter up to 10 locations separated by a comma.
- Click on the `Add` green button on the bottom right of the pop-up box.


**Webex Security Audit Events Input**

The **Webex Security Audit Events** input is used to fetch the data from [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events) endpoint. It allows users to retrieve user sign-in and sign-out data.

**Prerequisites**: This input is only available to customers with **Pro Pack** for Control Hub. To use this input, you must make sure you have **Pro Pack** for Webex Contol Hub, and then follow these two steps to enable this feature.
1. Sign in to Control Hub, then under **Management** > **Organization Settings**.
2. In the **User authentication data** section, toggle **Allow user authentication data** on.

The `Start Time` is required. Set the starting date and time to fetch admin audit events. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.

The `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. End Time must be after the Start Time.
- Click on the `Add` green button on the bottom right of the pop-up box.


**Webex Contact Center - Search**

The **Webex Contact Center - Search** input is used to fetch the data from [Webex Contact Center - Search](https://developer.webex.com/webex-contact-center/docs/api/v1/search/search) endpoint. It allows users to retrieve Agent Activity Record, Agent Session Record, Customer Activity Record, Customer Session Record.

**Prerequisites**: This input is only available to Webex Contact Cetner Administrator or Supervisor.

The `Start Time` is required. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). It cannot be older than 36 months from the current time. The first ingestion may pull a lot of data, please make sure you set a large interval when your Start Time is older than 1 month from current time.

The `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). The duration between Start Time and End Time must not be more than 365 days. Leave it blank if an ongoing ingestion mode is needed.

The `Query Template` is required. Please select the data source you wish to ingest into Splunk from the four options below. If you require all of them, please create four separate inputs.

- Agent Activity Record(AAR): Represents an atomic step in the agent workflow.
- Agent Session Record(ASR): Represents the agent workflow, consisting of a sequence of agent activities.
- Customer Activity Record(CAR): Represents an atomic step in the customer workflow.
- Customer Session Record(CSR): Represents the customer workflow, consisting of a sequence of customer activities.

For more information on each data source, please check [here](https://help.webex.com/en-us/article/tajemk/Cisco-Webex-Contact-Center-Analyzer-User-Guide#reference-template_2df0d0a4-4fac-4758-82a7-1fa59961b472).

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the end time of the last round as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds.
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Webex Contact Center Region(_required_)**: Select your Webex Contact Center Region.
    - **Org ID**(_required_): Enter your Webex Contact Center Orgnization ID.
    - **Start Time** (_required_): Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. 
    - **End Time** (_optional_): End date and time in the format YYYY-MM-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed.
    - **Query Template** (_required_): Select the appropriate Query Template for the data source you wish to ingest.
- Click on the `Add` green button on the bottom right of the pop-up box.

## Versions Supported

  - Tested for installation and basic ingestion on Splunk 9.X and 8.2.

> Built by Splunk's FDSE Team (#team-fdse).

## Reference 
- This Add-on was built via splunk-add-on-ucc-framework

## Credits & Acknowledgements
* Yuan Ling
* Marie Duran
* Ashley Hoang
* Isaac Fonseca
* Erica Pescio