# Webex Admin Audit Events Input 

The **Webex Admin Audit Events** input is used to fetch the data from [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events) endpoint. It allows users to retrieve organization-wide audit logs all over the account.

**Please Note**: Due to the API behavior, the selected time range cannot be more than a year. Therefore, If you want to obtain the audit logs that happened more than one year ago, you **MUST** fill in both `Start Time` and `End Time`, and ensure that the range does not exceed one year.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.


#### Query Parameters 
- `Start Time` is required. Set the starting date and time to fetch admin audit events. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-01-01T00:00:00.000Z). If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.
- `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-02-01T00:00:00.000Z).