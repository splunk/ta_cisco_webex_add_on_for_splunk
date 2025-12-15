# Webex Detailed Call History 

The **Webex Detailed Call History** input is used to fetch the data from [Webex Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history) endpoint. It allows users to retrieve detailed data from calls. Only organization administrators can retrieve the data and it requires the administrator role "Webex Calling Detailed Call History API access" to be enabled.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest call start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

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
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The Start Time **MUST** must be between 5 minutes ago and 48 hours ago.|
|`end_time`               |End Time                          |Optional, End date and time in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed. The End Time **MUST** be later than the Start Time but no later than 48 hours.|
|`location`               |Locations.                        |Optional, Enter up to 10 comma-separed locations. Each location name should the same as shown in the Control Hub.|