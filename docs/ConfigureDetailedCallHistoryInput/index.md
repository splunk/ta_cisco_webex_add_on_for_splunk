# Webex Detailed Call History 

The **Webex Detailed Call History** input retrieves detailed call records (CDRs) for your organization. Only organization administrators can retrieve the data, and it requires the administrator role "Webex Calling Detailed Call History API access" to be enabled.

The input collects data from two complementary Webex Calling Detailed Call History APIs — [CDR Feed](https://developer.webex.com/calling/docs/api/v1/reports-detailed-call-history/get-detailed-call-history) and [CDR Stream](https://developer.webex.com/calling/docs/api/v1/reports-live-stream-detailed-call-history/get-live-stream-detailed-call-history) — and switches between them automatically based on how old the data being collected is:

- **CDR Feed** (`/v1/cdr_feed`, history): can query any window between 5 minutes ago and 30 days ago, in up to 12-hour chunks per request. Used to backfill older records efficiently.
- **CDR Stream** (`/v1/cdr_stream`, near real-time): records become available about 1 minute after the call data reaches the Webex Calling cloud, but the start time cannot be older than 12 hours and only 2 hours of records can be pulled per request. Used for the most recent data once collection has caught up to near real-time.

Both APIs return the same records. A time chunk is served by **CDR Stream** once its start time is within 2 hours of now; anything older is served by **CDR Feed** in 12-hour chunks, capped at that 2-hour boundary so CDR Stream cleanly handles the recent remainder. To respect the CDR rate limits (1 initial request per minute), the input waits 60 seconds between chunks.

The input uses checkpointing to avoid ingesting duplicate data, and the saved checkpoint is used as the `Start Time` for the next run:

- **When a chunk returns new records**, the checkpoint is set to the maximum **Report time** of the records that were actually written. Because the Webex CDR `startTime` filter is inclusive at second granularity, any record whose Report time is at or before the saved checkpoint is skipped before indexing to prevent duplicates.
- **When a chunk returns no new records** (either genuinely empty or every record was skipped as a duplicate), the checkpoint is advanced using the chunk's **end time** so collection can move forward. For **CDR Stream** the checkpoint always advances to the chunk end. For **CDR Feed** the checkpoint advances to the chunk end only if the chunk is fully outside the 2-hour late-data buffer; if it straddles the buffer boundary it advances only to that boundary and stops, and if it falls entirely within the buffer the checkpoint is left unchanged so the window is retried on the next run.

## Configure Webex Detailed Call History input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Detailed Call History**.
3. Enter the information in the related fields using the following input parameters table.

## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`account_region`         |Webex Account Region              |Required. The region of you Webex account.|
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The Start Time **MUST** be no earlier than 30 days ago.|
|`end_time`               |End Time                          |Optional, End date and time in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The End Time **MUST** be later than the Start Time and at least 1 minute in the past.|
|`location`               |Locations.                        |Optional, Enter up to 10 comma-separed locations. Each location name should the same as shown in the Control Hub.|