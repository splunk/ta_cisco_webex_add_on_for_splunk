# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [v1.3.0] - 2025-10-23

### Added

- Added a new generic input that allows retrieving data from custom endpoints.

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
