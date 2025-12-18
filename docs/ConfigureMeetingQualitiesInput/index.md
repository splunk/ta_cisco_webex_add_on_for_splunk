# Webex Meeting Qualities

The **Webex Meeting Qualities** input is used to fetch the data from [Webex Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities) endpoint. It allows users to retrieve quality data for meetings. Only organization administrators can retrieve meeting quality data.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest meeting start time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

## Configure Webex Meeting Qualities input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Meeting Qualities**.
3. Enter the information in the related fields using the following input parameters table.

## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. The Start Time **MUST** be within 7 days from the current time.|
|`end_time`               |End Time                          |Optional, End date and time in the format YYYY-Mon-DDTHH:MM:SSZ. `example:2023-02-01T00:00:00Z`. Leave it blank if an ongoing ingestion mode is needed.|