# Cisco Webex Add on for Splunk

Here are the endpoints and their mapping soucetypes.
| Webex Endpoint                                                                                                   | Splunk Sourcetype               |
|-------------------------------------------------------------------------------------------------------------------------|---------------------------------|
| [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         |
| [Meeting Participants](https://developer.webex.com/docs/api/v1/meeting-participants/list-meeting-participants)                       | cisco:webex:meetings:participant             |

## Getting Started
### Installation Instructions
This Add-on can be installed in **Splunk Enterprise**. 

#### Installation Steps for `Splunk Enterprise`
- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Singleserverinstall) to install the Add-on in a single-instance Splunk Enterprise deployment.

- Please follow the steps [here](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall) to install the Add-on in a distributed Splunk Enterprise deployment.

### Create a Webex Integration
The Cisco Webex Add on for Splunk supports OAuth2 Authentication, which allows third-party integrations to get a temporary access token for authenticating API calls. Therefore, creating a Webex integration is required to work along with this Add-on. Please follow the following steps to create a dedicated Webex integration for this Add-on. Further documentation can be found [here](https://developer.webex.com/docs/integrations)
1. **Registering your Integration**: visit the [Webex for Developers](https://developer.webex.com/) select `My Webex Apps` from the menu under your avatar at the top of this page, click `Create a New App` then `Create an Integration` to start the wizard.
2. **Provide app related information**:
    - **Integration name**: Enter a name for yor integration. `e.g. Webex Integration for Splunk`
    - **Icon**: Upload your own or select from the defaults
    - **Description**: Provide some details about your integration
    - **Redirect URI(s)**: Follow the following steps to retrieve your Redirect URI:
        - Open **Cisco Webex Add on for Splunk** in Splunk. Go to `Configuration > Account > Add`. The Redirect URI will show up in the `Redirect url` field. Please copy and paste it to the `Redirect URI(s)` field in the Webex Integration.
        - **For Splunk Heavy Forwarders (or IDM)**: please replace the `{domain}` with the domain of your Splunk Heavy Forwarder (or IDM). For example, if the domain of your HF or IDM is `example.splunk.link`, then the Redirect URI you have to enter is:  `https://example.splunk.link/en-US/app/ta_cisco_webex_add_on_for_splunk/ta_cisco_webex_add_on_for_splunk_redirect`
    
    - **Scopes**. Please add the following scopes: 
        - `meeting:schedules_read` 
        - `meeting:participants_read`
5. Click **Add Integration** buttom on the bottom of the page, your `Client ID` and `Client Secret` are ready to use. 

### Configuration Instructions
Open the Web UI for the Heavy Forwarder (or IDM). Access the Add-on from the list of applications. Please follow the following steps in order:

#### 1. Create Account
- Click on the `Configuration` button on the top left corner.
- Click on the `Account` button.
- Click on the `Add` button on the top right to create a new account.
-  Enter the following details in the pop-up box:
    - **Account name**: Enter a unique name for this account.
    - **Client ID**: Enter the `Client ID` that you obtained above here.
    - **Client Secret**: Enter the `Client Secret` that you obtained above here.
    - **Redirect URI**: The Redirect URI will auto show up. 
    - Click on the `Add` button.


#### 2. Create Input

The **webex_meetings** input is used to fetch the data from both [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings) endpoint and [Meeting Participants](https://developer.webex.com/docs/api/v1/meeting-participants/list-meeting-participants) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting participants.

**Please Note**: The input only returns the **historical** meeting reports and participant reports. The reports are only ingested into Splunk after the meetings have ended with a 12 hours delay to reduce data gaps.

The `Start Time` for fetching the meeting & participant reports **MUST** fall be at least 12 hours before the current date and time. For example, if today is 2021-06-01 12:00:00 UTC, the Start Time **CANNOT** be a date after 2021-06-01 00:00:00 UTC. The input will return an error message if the Start Time is set more than 12 hours before current date and time. If you leave it blank, the API will default to the last 7 days.

The `End Date` is optional. If you set it to be a specific date, only reports within the time range from Start Date to End Date will be ingested. If you leave it blank, the API will default to 7 days after start time; or the current date and time if Start Time is not set.

The `Interval` is the time interval (in seconds) to run the input and **MUST** be set to a number greater than or equal to 43200 (12 hours) to avoid collecting duplicate events. The input will return an error message if the interval is set to a number less than 43200.

- Click on the `Inputs` button on the top left corner.
- Click on `Create New Input` button on the top right corner.
- Enter the following details in the pop-up box:
    - **Name** (_required_): Unique name for the data input.
    - **Interval** (_required_): Time interval of input in seconds. Must be greater than or eqaul to 43200 (12 hours).
    - **Index** (_required_): Index for storing data.
    - **Global Account** (_required_): Select the account created during Configuration.
    - **Start Time** (_optional_): Start date and time (inclusive) in the format YYYY-Mon-DDTHH:MM:SSZ (example:2022-01-01T00:00:00Z). Start Time must be prior to 12 hours before current time. Default is last 7 days
    - **End Time** (_optional_): End date and time (exclusive) in the format YYYY-Mon-DDTHH:MM:SSZ. Default is 7 days after Start Time; or the current date and time if Start Time is not set. 
- Click on the `Add` green button on the bottom right of the pop up box.

## Versions Supported

  - Tested for installation and basic ingestion on Splunk 8.2 for **CentOS** system.

> Built by Splunk's FDSE Team (#team-fdse).

## Reference 
- This Add-on was built via splunk-add-on-ucc-framework

## Credits & Acknowledgements
* Yuan Ling
* Marie Duran
