# Prerequisites

The Cisco Webex Add-on for Splunk supports two authentication methods. Choose the one that best fits your environment and complete the corresponding prerequisite below:

- **Webex Integration - OAuth 2.0**: An admin authorizes the Add-on through an interactive browser-based consent flow. Best for standard deployments where an administrator can complete the OAuth authorization from the Splunk UI.
- **Webex Service App**: A machine-to-machine app that an organization administrator authorizes once. It does not require the interactive redirect flow, which makes it well suited for headless or restricted environments. You provide the Service App's Client ID, Client Secret, and the Access/Refresh Tokens generated after authorization.

Both methods use the OAuth 2.0 refresh-token grant, and the Add-on automatically refreshes the access token when it expires.

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

#### Create the Webex Service App in Webex

Alternatively, you can authenticate the Add-on using a **Webex Service App**. A Service App is authorized once by an organization administrator and does not require the interactive redirect flow. Further documentation can be found [here](https://developer.webex.com/docs/service-apps).

1. **Register your Service App**:
    - Visit [Webex for Developers](https://developer.webex.com/) and log in using your **Webex Admin Account**.
    - Select `My Webex Apps` from the menu under your avatar at the top of the page.
    - Click `Create a New App` then `Create a Service App` to start the wizard.
2. **Provide app related information**:
    - **Service App name**: Enter a name for your Service App. `e.g. Webex Service App for Splunk`
    - **Icon**: Upload your own or select from the defaults.
    - **Description**: Provide some details about your Service App.
    - **Scopes**: Select only the scopes you need, referring to the [scopes table above](#here-are-the-endpoints-their-corresponding-source-types-and-the-required-scopes).
3. Click **Create Service App**. Your `Client ID` and `Client Secret` are generated.
4. **Request admin authorization**: Submit the Service App for admin approval. Once an organization administrator authorizes it, generate the tokens.
5. **Generate tokens**: After authorization, use the Service App page to generate the `Access Token` and `Refresh Token`. Copy these values along with the `Client ID` and `Client Secret` — you will need all four when configuring the account in Splunk.


#### Here are the endpoints, their corresponding source types, and the required scopes.
| Splunk Input       | Webex Endpoint        | Splunk Sourcetype               | Required Scopes                 |
|--------------------|-----------------------|---------------------------------|---------------------------------|
| Webex Generic Endpoint                | [Webex API](https://developer.webex.com/messaging/docs/basics)                       | cisco:webex:<**API Endpoint**>       | Refer to the endpoint documentation to confirm the required scopes      |
| Webex Scheduled Meetings       | [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         | meeting:admin_schedule_read spark-admin:people_read   |
| Webex Meetings Summary Report       | [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports)                       | cisco:webex:meeting:usage:reports         | meeting:admin_schedule_read meeting:admin_participants_read meeting:admin_config_read   |
| Webex Meetings Summary Report       | [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports)                       | cisco:webex:meeting:attendee:reports             | meeting:admin_schedule_read meeting:admin_participants_read meeting:admin_config_read  |
| Webex Admin Audit Events       | [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events)                               | cisco:webex:admin:audit:events              | audit:events_read spark:organizations_read  |
| Webex Meeting Qualities       | [Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities)                               | cisco:webex:meeting:qualities              | analytics:read_all   |
| Webex Detailed Call History       | [CDR Feed](https://developer.webex.com/calling/docs/api/v1/reports-detailed-call-history/get-detailed-call-history) / [CDR Stream](https://developer.webex.com/calling/docs/api/v1/reports-live-stream-detailed-call-history/get-live-stream-detailed-call-history)                               | cisco:webex:call:detailed_history             | spark-admin:calling_cdr_read |
| Webex Security Audit Events       | [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events)                               | cisco:webex:security:audit:events            | audit:events_read spark:organizations_read |
| Webex Contact Center - Search       | [Webex Contact Center - Search](https://developer.webex.com/webex-contact-center/docs/api/v1/search/search)                               | cjp:config or cjp:config_read            | cisco:webex:contact:center:AAR cisco:webex:contact:center:ASR cisco:webex:contact:center:CAR cisco:webex:contact:center:CSR |

3. Click **Add Integration** on the bottom of the page, your `Client ID` and `Client Secret` are ready to use.



