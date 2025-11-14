# Webex Scheduled Meetings Input

The **Webex Scheduled Meetings** input is used to fetch the active scheduled meetings from [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings) endpoint. It allows users to retrieve account-wide scheduled meetings of all users in your organization.

**Note: In order to avoid ingesting duplicate meetings, each scheduled meeting will be only ingested when it reaches its start time. It doesn’t pull in the future scheduled meetings whose start time is in the future.**

#### Query Parameters 

- `meetingType: scheduledMeeting`
- `hostEmail: <HOST_EMAIL>`, where all HOST_EMAILs are getting from [List People](https://developer.webex.com/docs/api/v1/people/list-people) endpoint
- `Interval` is required. It's used to specify how often it hits the Webex Meetings endpoint to pull the scheduled meetings in. The ingestion time increase as the number of users increases. If you have more than 100 users in your organization, it's recommended to set the interval to be at least 300 (5 mins).
- `Start Time` is required. Set the starting date and time to fetch the scheduled meetings. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). This input aims to get active scheduled meetings, it's recommended to set Start Time to the current time. For example, the current time is `2023-08-01T10:05:28Z`, you can set it as `2023-08-01T00:00:00Z`. If you'd like to get all historical meetings, please use the **Webex Meetings Summary Report Input**.
- `End Time` is optional. If you set it to be a specific date, only the scheduled meetings within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z).
