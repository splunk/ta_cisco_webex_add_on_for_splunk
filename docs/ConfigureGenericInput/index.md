# Webex Generic Endpoint 

The **Webex Generic Endpoint** provides the flexibility to create a custom input using the Webex API endpoint of your choice. If you encounter scenarios where the predefined input options do not meet your requirements, you can use this option to enable data ingestion from a different source.


Keep in mind that the endpoint you want to use may require special permissions, roles, and/or scopes. Please refer to the API documentation to see the requirements needed to enable data ingestion for the endpoint.

Enter a `Start Time` whenever it is supported by the endpoint to help avoid duplicates. If an `End Time` is specified, data will be fetched up to that time; otherwise, data will be fetched up to the current time. If a `Start` or `Created` time is present in the response, it will be saved as a checkpoint and used as the `Start Time` for the next run.

Some endpoints require specific query parameters to function correctly. Users can add these parameters using the `Query Params` field. The input also supports path parameters in the URL, which should be included in the `API Endpoint` field.

## Configure Webex Generic Endpoint input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Generic Endpoint**.
3. Enter the information in the related fields using the following input parameters table.

## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`webex_endpoint`         |API Endpoint                      |The Webex API endpoint. It is not necessary to include a leading slash as for example: `device`, or `devices/12345678`.|
|`webex_base_url`         |Webex Base API URL                |Enter the base URL for the endpoint. Most Webex APIs use `webexapis.com`, but some may require a different base URL. For example, endpoints that require the `analytics:read_all` scope often use `analytics.webexapis.com`. Always refer to the endpoint documentation to confirm the correct base URL.|
|`start_time`             |Start Time                        |Required, Inclusive start date and time in the format `YYYY-MM-DDTHH:MM:SSZ`, e.g. `2023-01-01T00:00:00Z`.  Be aware of the endpoint limitations and valid ranges.|
|`end_time`               |End Time                          |Optional, End date and time in the format `YYYY-Mon-DDTHH:MM:SSZ`, e.g. `2023-02-01T00:00:00Z`. Leave blank if an ongoing ingestion mode is needed. Be aware of the endpoint limitations and valid ranges.|
|`query_params. `         |Query Params                      |Include any query parameters for the endpoint. For multiple parameters, enter them as comma-separated values (e.g. `locationId=0000000, messageId=0000000, teamId=0000000`).|