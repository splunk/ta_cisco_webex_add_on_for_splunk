# Contributing

Thank you for your interest in this project! ❤️ 🚀

For reporting unexpected behavior, documentation gaps, entirely new features, please open an [issue](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/issues)

Contributions via pull requests are also welcome:
* Create a branch for the issue / new feature
* Make your changes on your branch
* Open a [pull request](https://github.com/splunk/ta_cisco_webex_add_on_for_splunk/pulls)
* Add as reviewers [lingy1028](https://github.com/lingy1028), [@ifonsecam](https://github.com/ifonsecam) and [@ahoang-splunk](https://www.github.com/ahoang-splunk)

## Development Guidelines
This Add-on was built using the [UCC framework](https://splunk.github.io/addonfactory-ucc-generator/).

```bash
# Enable Virtual Environment
python3 -m venv .venv
source .venv/bin/activate;

# Build the add-on
APP_VERSION=$(cat globalConfig.json | jq -r '.meta.version') && \
ucc-gen build --ta-version $(APP_VERSION)

# Package the Add-On
ucc-gen package --path output/ta_cisco_webex_add_on_for_splunk
```

:book: [Command options](https://splunk.github.io/addonfactory-ucc-generator/commands/).

## Release the Add-On
A CI/CD workflow will automatically create a release. To trigger it:

- Bump the Add-On version according to [Semantic Versioning](http://semver.org/) in `package/app.manifest` and `globalConfig.json`
- Update the `CHANGELOG` following [guidelines](#changelog)
- Push to `main`

On push to `main`, the following checks will be executed before releasing a new version of the Add-On:

- **Build**: Creates app package
- **Sanity Check**: Validates version consistency between the `CHANGELOG` file and the Add-On. They must match.

### Changelog
A `CHANGELOG.md` file is used to document changes between versions. The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).
