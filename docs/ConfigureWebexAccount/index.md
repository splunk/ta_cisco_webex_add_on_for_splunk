# Set up your Webex Account in Splunk



1. Open the Web UI for the Heavy Forwarder (or IDM). Access the Add-on from the list of applications. 
2. Click on the `Configuration` tab on the top left corner.
3. Click on the `Account` button.
4. Click on the `Add` button on the top right to create a new account.
5. Enter the following details in the pop-up box:
    - **Account name**: Enter a unique name for this account.
    - **Webex API Base Endpoint**: Enter your Webex API Base Endpoint. The default one is `webexapis.com`.
    - **Auth Type**: Select the authentication method for this account:
        - **Webex Integration - OAuth 2.0**: Use the interactive OAuth authorization flow with a Webex Integration.
        - **Webex Service App**: Use the credentials generated from an authorized Webex Service App.
    - **Gov Account**: Please check this box if you are using a Webex Gov Account.

    #### If you selected **Webex Integration - OAuth 2.0**, provide:
    - **Client ID**: Enter the `Client ID` that you obtained from your Webex Integration.
    - **Client Secret**: Enter the `Client Secret` that you obtained from your Webex Integration.
    - **Redirect URI**: The Redirect URI will auto show up.
    - **Scopes**: Select the authorization scopes. Please ensure that the scopes entered here match those selected in your Webex Integration.

    #### If you selected **Webex Service App**, provide:
    - **Client ID**: Enter the `Client ID` of your Webex Service App.
    - **Client Secret**: Enter the `Client Secret` of your Webex Service App.
    - **Access Token**: Enter the `Access Token` generated after an administrator authorizes the Service App.
    - **Refresh Token**: Enter the `Refresh Token` generated after an administrator authorizes the Service App. It is used to automatically obtain new access tokens.
6. Click on the `Add` button.