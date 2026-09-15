# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [v1.5.1] - 2026-09-15

### Fixed

- Fixed duplicate ingestion in the Detailed Call History input where the CDR Stream checkpoint could get stuck on the most recent record. The Webex CDR `startTime` filter is inclusive at second granularity, so the record at the checkpoint boundary was returned and re-ingested on every run. Records at or before the saved checkpoint are now skipped before indexing, and timestamp comparisons use `datetime` (instead of string) so varying millisecond precision is ordered correctly.

## [v1.5.0] - 2026-09-08

### Added

- Added near real-time collection for the Detailed Call History input using the Webex CDR Stream API. The input now automatically switches between the CDR Feed API (history) and the CDR Stream API (near real-time) based on how old the data being collected is.

### Changed

- Aligned the Detailed Call History input with the updated CDR Feed API behavior: 30-day lookback window, 12-hour maximum query window per request, and filtering by Report time.
- Split the collection into per-request time windows based on the endpoint: the CDR Feed API uses a 12-hour window, while the CDR Stream API uses a 2-hour window.
- Updated the checkpoint logic for the Detailed Call History input to use the maximum Report time when a chunk has data and to advance safely on empty chunks, with a late-data buffer for the CDR Feed API.
- Added rate-limit handling for the CDR APIs, including a 60-second delay between chunks, pagination throttling, and retry on HTTP 429 responses using the Retry-After header.
- Updated input validation and UI help text for the Detailed Call History input start time (up to 30 days) and end time (at least 1 minute in the past).

## [v1.4.3] - 2026-07-02

### Fixed

- Fixed the "'bytes' object has no attribute 'encode'" error when using a proxy with credentials by bundling httplib2 0.22.0 with the add-on.

## [v1.4.2] - 2026-05-28

### Fixed

- Updated the FQDN link for Webex Meeting Qualities API.

## [v1.4.1] - 2026-05-11

### Fixed

- Fixed the FQDN link for Webex Detailed Call History API specifically for FedRAMP/Gov accounts.

## [v1.4.0] - 2026-02-27

### Added

- Added support for POST method in the Generic Input
- Added support for search endpoint of Webex Contact Center

## [v1.3.4] - 2026-03-30

### Fixed

- Fixed the Invalid Refresh Token issue by removing the retry logic inside API call.

## [v1.3.3] - 2026-03-30

### Fixed

- Added a validation to build new URL for the Detailed Call History input.
- Updated checkpoint logic for Detailed Call History input.

## [v1.3.2] - 2026-02-24

### Changed

- Refactored input file logic to use helper functions for token validation and time handling.
- Standardized all date formats across all the inputs.
- Updated documentation to reflect the date format standardization.

## [v1.3.1] - 2025-12-27

### Fixed

- Added a 24‑hour ingestion delay to the Webex summary report input to prevent attendee data loss.
- Updated input validation to use UTC time.

## [v1.3.0] - 2025-10-23

### Added

- Added a new generic input that allows retrieving data from custom endpoints.
- Added a new field to the account configuration to indicate whether it is a Gov account.

### Changed

- Minor updates to globalConfig.json – bumped schemaVersion to 0.0.10

## [v1.2.0] - 2025-09-30

### Added

- Added a multi-select Scope field to the UI.

### Changed

- Removed the redudant app.conf.
- Minor updates to globalConfig.json – removed redundant 'oauth_field' keys.

## [v1.1.0] - 2025-09-08

### Added

- New input to retrieve data from the Security Audit Events endpoint.

### Changed

- Replaced the deprecated UTC Python Function.
- Minor updates in app.conf.

## [v1.0.11] - 2025-08-25

### Fixed

- Pagination bug.

### Changed

- Updated the pagination logic to use the next page link directly, instead of extracting specific parameters.

## [v1.0.10] - 2025-06-19

### Fixed

- Fixed the timeout issue for List People endpoint in the the Webex Scheduled Meetings Input.
- Fixed the proxy issue on the OAuth flow.
- Fixed the AppInspect Failures.

## [v1.0.9] - 2025-05-09

### Added

- New input to retrieve data from the Webex Detailed Call History endpoint.

## [v1.0.8] - 2025-05-07

### Added

- Cloud Compliant.

### Changed

- Upgraded Splunk UCC Framework.
- Upgraded Splunk-SDK.

## [v1.0.7] - 2024-11-13

### Removed

- `output` dir, `.tar*` and `.tgz` files.
