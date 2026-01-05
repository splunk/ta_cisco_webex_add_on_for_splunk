# Cisco Webex Add-on for Splunk

[![GitHub issues](https://img.shields.io/github/issues/splunk/ta_cisco_webex_add_on_for_splunk?label=issues&color=informational)](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/issues)
[![GitHub All Releases](https://img.shields.io/github/downloads/splunk/ta_cisco_webex_add_on_for_splunk/total?label=download&logo=github&style=flat-square&color=important)](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/releases)
[![Latest release (latest by date)](https://img.shields.io/github/v/release/splunk/ta_cisco_webex_add_on_for_splunk?label=Latest%20Release)](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/releases)
[![License](https://img.shields.io/badge/License-Apache_2.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)

Find more details in our [Github Page](https://splunk.github.io/ta_cisco_webex_add_on_for_splunk/) and [README](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/blob/main/package/README.md#here-are-the-endpoints-their-corresponding-source-types-and-the-required-scopes)
> **Cisco Webex Add-on for Splunk** is an Add-on to pull in data from _[Webex REST API](https://developer.webex.com/docs/basics)_ to Splunk.

Here are the endpoints and their mapping soucetypes.
| Splunk Input       | Webex Endpoint        | Splunk Sourcetype               |
|--------------------|-----------------------|---------------------------------|
| Webex Scheduled Meetings       | [Meetings](https://developer.webex.com/docs/api/v1/meetings/list-meetings)                       | cisco:webex:meetings         |
| Webex Meetings Summary Report       | [Meeting Usage Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-usage-reports)                       | cisco:webex:meeting:usage:reports         |
| Webex Meetings Summary Report       | [Meeting Attendee Reports](https://developer.webex.com/docs/api/v1/meetings-summary-report/list-meeting-attendee-reports)                       | cisco:webex:meeting:attendee:reports             |
| Webex Admin Audit Events       | [Admin Audit Events](https://developer.webex.com/docs/api/v1/admin-audit-events)                               | cisco:webex:admin:audit:events               |
| Webex Meeting Qualities       | [Meeting Qualities](https://developer.webex.com/docs/api/v1/meeting-qualities/get-meeting-qualities)                               | cisco:webex:meeting:qualities              |
| Webex Detailed Call History       | [Detailed Call History](https://developer.webex.com/docs/api/v1/reports-detailed-call-history/get-detailed-call-history)                               | cisco:webex:call:detailed_history             |
| Webex Security Audit Events       | [Security Audit Events](https://developer.webex.com/admin/docs/api/v1/security-audit-events/list-security-audit-events)                               | cisco:webex:security:audit:events            |
| Webex Generic Endpoint                | [Webex API](https://developer.webex.com/messaging/docs/basics)                       | cisco:webex:<**API Endpoint**>       |

## Versions Supported

  - Tested for installation and basic ingestion on Splunk 10.x, 9.X and 8.2.

> Built by Splunk's FDSE Team (#team-fdse).

## Credits & Acknowledgements
* Yuan Ling
* Isaac Fonseca Monge
* Marie Duran
* Ashley Hoang
* Erica Pescio
