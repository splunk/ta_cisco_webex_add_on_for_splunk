# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Fixed

- `webex_meetings` input re-ingested every meeting on every interval whenever a single host's meetings request failed (e.g. a Webex `502`). The checkpoint is saved only after the entire per-host loop completes, so one failing host aborted the run before `save_check_point()`, leaving the checkpoint unset and the dedup comparison permanently falling back to `start_time`. The per-host fetch and write now log and continue instead of raising, so the checkpoint advances and duplicate ingestion stops.
- `webex_meeting_qualities` input had the same defect in its per-meeting loop: the checkpoint is saved only after the entire loop completes, so a single meeting's qualities request failing aborted the run before `save_check_point()`. This is triggered permanently rather than transiently — quality data expires 14 days after a meeting, after which `GET /v1/meeting/qualities` returns `425` ("Quality data is not available for this meeting because it has expired after 14 days") for that meeting on every run. With the checkpoint pinned, every meeting in the window was re-ingested every interval. The per-meeting qualities fetch and write now log and continue instead of raising, so the checkpoint advances past expired/failing meetings and duplicate ingestion stops.

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
