# Webex Security Audit Events Input 

The **Webex Security Audit Events** input is used to fetch the data from [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events) endpoint. It allows users to retrieve user sign-in and sign-out data.

**Prerequisites**: This input is only available to customers with **Pro Pack** for Control Hub. To use this input, you must make sure you have **Pro Pack** for Webex Contol Hub, and then follow these two steps to enable this feature.
1. Sign in to Control Hub, then under **Management** > **Organization Settings**.
2. In the **User authentication data** section, toggle **Allow user authentication data** on.

The input uses checkpointing to avoid ingesting duplicate data. After the initial run, the script will save the latest audit event created time as the checkpoint, and will be used as the `Start Time` (advancing by one millisecond) for the next run.

## Configure Webex Security Audit Events input through Splunk Web 

1. In the **Inputs** tab select **Create New Input**.
2. Choose **Webex Security Audit Events**.
3. Enter the information in the related fields using the following input parameters table.

## Input Parameters 

Each attribute in the following table corresponds to a field in Splunk Web.

|Input name               |Corresponding field in Splunk Web | Description|
|-------------------------|----------------------------------|------------|
|`name`                   |Name                              |A unique name for your input.|
|`interval`               |Interval                          |Time interval of input in seconds.|
|`index`                  |Index                             |The index in which the data should be stored. The default is <code>default</code>.|
|`account`                |Global Account                    |The Webex account created in the Configuration tab.|
|`start_time`             |Start Time                        |Required, Start date and time (inclusive) in the format YYYY-MM-DDTHH:MM:SSZ, `example:2023-01-01T00:00:00Z`. If you leave the `End Time` blank, Start Time **MUST** be within one year from the current time.|
|`end_time`               |End Time                          |Optional, End date and time in the format YYYY-Mon-DDTHH:MM:SSZ. `example:2023-02-01T00:00:00Z`. End Time must be after the Start Time.|