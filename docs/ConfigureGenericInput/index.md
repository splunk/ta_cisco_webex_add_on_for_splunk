# Webex Generic Endpoint 

The **Webex Generic Endpoint** provides the flexibility to create a custom input using the Webex API endpoint of your choice. If you encounter scenarios where the predefined input options do not meet your requirements, you can use this option to enable data ingestion from a different source.

Click on `Webex API Input` to enable this input

Keep in mind that the endpoint you want to use may require special permissions, roles, and/or scopes. Please refer to the API documentation to see the requirements needed to enable data ingestion for the endpoint.

Enter a `Start Time` whenever it is supported by the endpoint to help avoid duplicates. If an `End Time` is specified, data will be fetched up to that time; otherwise, data will be fetched up to the current time. If a `Start` or `Created` time is present in the response, it will be saved as a checkpoint and used as the `Start Time` for the next run.

Some endpoints require specific query parameters to function correctly. Users can add these parameters using the `Query Params` field. The input also supports path parameters in the URL, which should be included in the `API Endpoint` field.

#### Query Parameters 
- `API Endpoint` is required. Specify the Webex API endpoint, it is not necessary to include a leading slash as for example: `device`, or `devices/12345678`.
- `Webex Base API URL` is required. Enter the base URL for the endpoint. Most Webex APIs use `webexapis.com`, but some may require a different base URL. For example, endpoints that require the `analytics:read_all` scope often use `analytics.webexapis.com`. Always refer to the endpoint documentation to confirm the correct base URL.
- `Start Time` is optional. Set the inclusive start date and time in the format YYYY-MM-DDTHH:MM:SSZ, e.g. 2023-01-01T00:00:00Z.  Be aware of the endpoint limitations and valid ranges.
- `End Time` is optional.  End date and time in the format YYYY-Mon-DDTHH:MM:SSZ, e.g. 2023-02-01T00:00:00Z. Leave blank if an ongoing ingestion mode is needed. Be aware of the endpoint limitations and valid ranges.
- `Query Params` is optional. Include any query parameters for the endpoint. For multiple parameters, enter them as comma-separated values (e.g. locationId=0000000, messageId=0000000, teamId=0000000).