# Prerequisites


#### Create the Webex OAuth Integration in Webex

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
        - **For Splunk Heavy Forwarders (or IDM)**: please replace the `{domain}` with the domain of your Splunk Heavy Forwarder (or IDM). For example, if the domain of your HF or IDM is `example.splunk.link`, then the Redirect URI you have to enter is:  `https://example.splunk.link/en-US/app/ta_cisco_webex_add_on_for_splunk/ta_cisco_webex_add_on_for_splunk_redirect`. Ensure not to submit the form yet.
    
    - **Scopes**: Please select only the scopes you need referring to the table below

    #### Here are the endpoints, their corresponding source types, and the required scopes.
| Splunk Input       | Webex Endpoint        | Splunk Sourcetype               | Required Scopes                 |
|--------------------|-----------------------|---------------------------------|---------------------------------|
| Webex Scheduled Meetings       | [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         | meeting:admin_schedule_read spark-admin:people_read   |
| Webex Meetings Summary Report       | [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports)                       | cisco:webex:meeting:usage:reports         | meeting:admin_schedule_read meeting:admin_participants_read   |
| Webex Meetings Summary Report       | [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports)                       | cisco:webex:meeting:attendee:reports             | meeting:admin_schedule_read meeting:admin_participants_read   |
| Webex Admin Audit Events       | [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events)                               | cisco:webex:admin:audit:events              | audit:events_read spark:organizations_read  |
| Webex Meeting Qualities       | [Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities)                               | cisco:webex:meeting:qualities              | analytics:read_all   |
| Webex Detailed Call History       | [Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history)                               | cisco:webex:call:detailed_history             | spark-admin:calling_cdr_read |
| Webex Security Audit Events       | [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events)                               | cisco:webex:security:audit:events            | audit:events_read spark:organizations_read |

3. Click **Add Integration** on the bottom of the page, your `Client ID` and `Client Secret` are ready to use.


#### Set up your Webex Account in Splunk
- Open the Web UI for the Heavy Forwarder (or IDM). Access the Add-on from the list of applications. 
- Click on the `Configuration` tab on the top left corner.
- Click on the `Account` button.
- Click on the `Add` button on the top right to create a new account.
-  Enter the following details in the pop-up box:
    - **Account name**: Enter a unique name for this account.
    - **Webex API Base Endpoint**: Enter your Webex API Base Endpoint. The default one is `webexapis.com`.
    - **Client ID**: Enter the `Client ID` that you obtained above here.
    - **Client Secret**: Enter the `Client Secret` that you obtained above here.
    - **Redirect URI**: The Redirect URI will auto show up. 
    - **Scopes**: Select the authorization scopes. Please ensure that the scopes entered here match those selected in your Webex Integration.
    - **Gov Account**: Please check this box if you are using a Webex Gov Account. 
- Click on the `Add` button.