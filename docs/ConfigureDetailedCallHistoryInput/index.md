# Webex Detailed Call History 

The **Webex Detailed Call History** input is used to fetch the data from [Webex Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history) endpoint. It allows users to retrieve detailed data from calls. Only organization administrators can retrieve the data and it requires the administrator role "Webex Calling Detailed Call History API access" to be enabled.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest call start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

#### Query Parameters 
- `Start Time` is required. Set the starting date and time to fetch the calls data. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SSZ (example:2023-01-01T00:00:00Z). The Start Time **MUST** must be between 5 minutes ago and 48 hours ago, more than that is not possible.
- `End Time` is optional. If you set it to be a specific date, only data within the time range from Start time to End time will be ingested. The format should be YYYY-MM-DDTHH:MM:SSZ (example:2023-02-01T00:00:00Z). Leave it blank if an ongoing ingestion mode is needed. The End Time **MUST** be later than the Start Time but no later than 48 hours.
- `Locations` field is optional. You can include up to 10 comma-separed locations, and each location name should the same as shown in the Control Hub.