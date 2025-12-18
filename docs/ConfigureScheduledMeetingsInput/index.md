# Webex Scheduled Meetings Input

The **Webex Scheduled Meetings** input is used to fetch the active scheduled meetings from [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings) endpoint. It allows users to retrieve account-wide scheduled meetings of all users in your organization.

Query parameters used for this input:
- `meetingType: scheduledMeeting`
- `hostEmail: <HOST_EMAIL>`, where all HOST_EMAILs are getting from [List People](https://developer.webex.com/docs/api/v1/people/list-people) endpoint

**Note: In order to avoid ingesting duplicate meetings, each scheduled meeting will be only ingested when it reaches its start time. It doesn’t pull in the future scheduled meetings whose start time is in the future.**

## Configure Webex Scheduled Meetings input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Scheduled Meetings**.
3. Enter the information in the related fields using the following input parameters table.


## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Interval is used to specify how often it hits the Webex Meetings endpoint to pull the scheduled meetings in. The ingestion time increase as the number of users increases. If you have more than 100 users in your organization, it's recommended to set the interval to be at least 300 (5 mins).|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ. It's recommended to set Start Time to the current time. For example, the current time is `2023-08-01T10:05:28Z`, you can set it as `2023-08-01T00:00:00Z`.|
|`end_time`               |End Time                          |Optional, if you set it to be a specific date, only the scheduled meetings within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).|