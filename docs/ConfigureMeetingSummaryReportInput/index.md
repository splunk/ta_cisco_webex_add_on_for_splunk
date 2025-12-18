# Webex Meetings Summary Report Input

The **Webex Meetings Summary Report** input is used to fetch the data from both [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports) endpoint and [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting attendees.

**Please Note**: The input only returns the **historical** meeting reports and attendee reports, since these two endpoints only contain historical data. The input includes a 24‑hour delay due to the behavior of the API. According to the Webex documentation, “The report data for a meeting should be available within 24 hours after the meeting ends.” To ensure the data is complete and to avoid data gaps, the input ingests meeting data only after a full 24 hours have passed since the meeting ended.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one second) for the next run.

## Configure Webex Meeting Summary input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Meetings Summary Report**.
3. Enter the information in the related fields using the following input parameters table.

## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`site_url`               |Site Name                         |Site Name of the Webex Meeting account. `example: example.webex.com`|
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The start time must be set to 24 hours prior to the current UTC time. The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.|
|`end_time`               |End Time                          |Optional, End date and time in the format YYYY-Mon-DDTHH:MM:SSZ.(Optional), `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The interval between Start Time and End Time cannot exceed 30 days.|