# Webex Meeting Qualities

The **Webex Meeting Qualities** input is used to fetch the data from [Webex Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities) endpoint. It allows users to retrieve quality data for meetings. Only organization administrators can retrieve meeting quality data.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

#### Query Parameters 
- `Start Time` is required. Set the starting date and time to fetch meeting quality data. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). Due to the Webex API limitation, Quality information may be retrieved for up to 7 days. The Start Time **MUST** be within 7 days from the current time.
- `End Time` is optional. If you set it to be a specific date, only data within the time range from Start time to End time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). Leave it blank if an ongoing ingestion mode is needed.
