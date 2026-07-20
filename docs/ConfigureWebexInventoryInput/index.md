# Webex Inventory Input

The **Webex Inventory** input allows you to make requests to any Webex API endpoint on a fixed interval and index the response as events. This input is designed for inventory-style endpoints that return a collection of resources (e.g., devices, locations, workspaces, people).

## Key Features

- **Flexible Endpoint Support**: Query any Webex API endpoint using GET or POST requests
- **Custom Query Parameters**: Add query parameters to filter or customize API requests
- **Request Body Support**: Include JSON payloads for POST requests
- **Batch Processing**: Each run is tagged with a unique, sortable batch_id (epoch timestamp) for easy correlation
- **Fixed Interval**: Configure how often the endpoint is queried
- **No Deduplication**: Every run re-indexes the full response, making it ideal for tracking inventory changes

## Important Notes

- **No Checkpointing**: This input does not maintain state between runs, so the full response from the API is re-indexed on each interval
- **No Deduplication**: Each scheduled run will re-index all returned items from the API endpoint
- **Ideal for Inventory**: This input is best suited for endpoints that return complete collections of resources that don't change frequently
- **Batch ID**: All events from a single run include the same batch_id, allowing you to correlate events and identify when they were collected

## Configure Webex Inventory input through Splunk Web

1. In the **Inputs** tab, select **Create New Input**
2. Choose **Webex Inventory**
3. Enter the information in the related fields using the following input parameters table

## Input Parameters

Each attribute in the following table corresponds to a field in Splunk Web.

| Input Name | Corresponding Field in Splunk Web | Description |
|---|---|---|
| `name` | Name | A unique name for your input. Must start with a letter and be followed by alphanumeric characters or underscores. Maximum length is 100 characters. |
| `interval` | Interval | Time interval (in seconds) at which the Webex API endpoint will be queried. |
| `index` | Index | The Splunk index where the data should be stored. Default is `default`. |
| `global_account` | Global Account | The Webex account created in the Configuration tab. |
| `webex_base_url` | Webex Base API URL | The base URL for the Webex API endpoint. Usually `webexapis.com`, but some endpoints may require different base URLs (e.g., `analytics.webexapis.com` for analytics-related endpoints). Refer to the endpoint documentation for the correct URL. Default: `webexapis.com`. |
| `webex_endpoint` | API Endpoint | The Webex API endpoint to query. Do not include a leading slash. Examples: `devices`, `devices/12345678`, `workspaces`, `locations`, `people`. |
| `method` | Request Method | The HTTP method to use: `GET` (default) or `POST`. Most endpoints use GET; use POST only if the endpoint documentation specifies it. |
| `query_params` | Query Params | Optional comma-separated query parameters to include in the API request. Each parameter will be appended to the URL. Example: `max=500, type=RoomDevice` |
| `request_body` | Request Body | Optional JSON-formatted request body for POST requests. Example: `{"query":"query { devices(type: CONTROLLER) { hostName ipAddress version } }"}` |
| `sourcetype` | Sourcetype | A sourcetype name for the data input. This helps identify the data in Splunk searches. |

## Usage Examples

### Example 1: Fetch All Devices

**Input Configuration:**
- Name: `fetch_webex_devices`
- Interval: `3600` (1 hour)
- Index: `default`
- Global Account: `my_webex_account`
- Webex Base API URL: `webexapis.com`
- API Endpoint: `devices`
- Request Method: `GET`
- Sourcetype: `cisco:webex:inventory:devices`

This configuration fetches the list of all Webex devices every hour.

### Example 2: Fetch Workspaces with Query Parameters

**Input Configuration:**
- Name: `fetch_webex_workspaces`
- Interval: `1800` (30 minutes)
- Index: `default`
- Global Account: `my_webex_account`
- Webex Base API URL: `webexapis.com`
- API Endpoint: `workspaces`
- Request Method: `GET`
- Query Params: `max=500`
- Sourcetype: `cisco:webex:inventory:workspaces`

This configuration fetches workspaces with a maximum of 500 results every 30 minutes.

### Example 3: Fetch Locations

**Input Configuration:**
- Name: `fetch_webex_locations`
- Interval: `7200` (2 hours)
- Index: `default`
- Global Account: `my_webex_account`
- Webex Base API URL: `webexapis.com`
- API Endpoint: `locations`
- Request Method: `GET`
- Sourcetype: `cisco:webex:inventory:locations`

This configuration fetches all locations every 2 hours.

## Returned Event Structure

Each item returned by the API endpoint is indexed as a separate event. The event includes:

- All fields from the API response
- `batch_id`: A unique identifier for the batch run (epoch milliseconds)
- `webex_endpoint`: The endpoint that was queried

**Example event:**
```json
{
  "id": "abc123def456",
  "displayName": "My Device",
  "type": "RoomDevice",
  "product": "Board",
  "deviceType": "ROOM_DEVICE",
  "batch_id": "1672531200000",
  "webex_endpoint": "devices"
}
```

## Best Practices

1. **Appropriate Intervals**: Use intervals that match your organization's needs. Frequent queries may impact API rate limits.
2. **Query Parameters**: Use query parameters to limit the data returned (e.g., `max=500`) to improve performance.
3. **Sourcetype Naming**: Use descriptive sourcetype names that clearly indicate the endpoint and data type being collected.
4. **Monitoring**: Monitor input logs to ensure the input is running successfully and check for any API errors or validation failures.
5. **Batch ID Correlation**: Use the `batch_id` field in your searches to identify and correlate all events from a single collection run.

## Troubleshooting

### Common Issues

**Invalid JSON in Query Params or Request Body**
- Ensure all JSON is properly formatted and valid
- Use double quotes for JSON string values
- Escape special characters appropriately

**API Endpoint Not Found**
- Verify the API endpoint name is correct
- Check the Webex API documentation for the correct endpoint path
- Ensure the Webex Base API URL is correct for the endpoint

**Authentication Errors**
- Verify the Global Account credentials are correct
- Check that the associated OAuth token has the required scopes for the endpoint
- Consult the Webex API documentation for required scopes

**Rate Limiting**
- If you see rate limit errors, increase the interval between queries
- Use query parameters to reduce the amount of data returned per request

## Related Resources

- [Webex API Documentation](https://developer.webex.com/docs/basics)
- [Webex OAuth Documentation](https://developer.webex.com/docs/integrations)
