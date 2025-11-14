# Webex Meetings Summary Report Input

The **Webex Meetings Summary Report** input is used to fetch the data from both [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports) endpoint and [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports) endpoint. It allows users to retrieve account-wide reports on past meetings and their correlated meeting attendees.

**Please Note**: The input only returns the **historical** meeting reports and attendee reports, since these two endpoints only contain historical data. The input will have a few hours delay due to the API behavior. Typically, meeting data is not showing up in the API until 2 to 3 hours after the meetings end. Therefore, the meetings data is only ingested 2 to 3 hours after the meetings end.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one second) for the next run.

#### Query Parameters 
- `Site Name` is required. Input the Site Name of the Webex Meeting account. Example: `example.webex.com`
- `Start Time` is required. Set the starting date and time to fetch meetings & attendees. The Start Time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). The interval between Start Time and End Time cannot exceed 30 days and Start Time cannot be earlier than 90 days ago.
- `End Time` is optional. If you set it to be a specific date, only reports within the time range from Start Time to End Time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). The interval between Start Time and End Time cannot exceed 30 days. Leave it blank if an ongoing ingestion mode is needed.
