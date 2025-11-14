# Webex Security Audit Events Input 

The **Webex Security Audit Events** input is used to fetch the data from [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events) endpoint. It allows users to retrieve user sign-in and sign-out data.

**Prerequisites**: This input is only available to customers with **Pro Pack** for Control Hub. To use this input, you must make sure you have **Pro Pack** for Webex Contol Hub, and then follow these two steps to enable this feature.
1. Sign in to Control Hub, then under **Management** > **Organization Settings**.
2. In the **User authentication data** section, toggle **Allow user authentication data** on.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

#### Query Parameters 
- `Start Time` is required. Set the starting date and time to fetch admin audit events. The Start time is inclusive and should be in the format YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-01-01T00:00:00.000Z). If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.
- `End Time` is optional. If you set it to be a specific date, only logs within the time range from Start Date to End Date will be ingested. The format should be YYYY-MM-DDTHH:MM:SS.SSSZ (example:2023-02-01T00:00:00.000Z).