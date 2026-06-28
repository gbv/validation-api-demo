# Validation Service

[![Docker image](https://github.com/gbv/validation-api-ws/actions/workflows/docker.yml/badge.svg)](https://github.com/orgs/gbv/packages/container/package/validation-api-ws)
[![Test](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml/badge.svg)](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml)

> Demo of a simple Web API to validate data against predefined criteria

This web service implements a **[Data Validation API](#API)** being specified as part of project AQinDA. The API helps allows to check data against application profiles and to integrate such checks into data processing workflows. The API is *not* meant to define quality criteria of application profiles but to execute defined qualitiy criteria in form of schema validation or other constraints.

Dependending on [configuration](#configuration) data can be passed via HTTP GET and POST, via URL, or from local files at the server. The result of analysis is returned as list of errors in [Data Validation Report Format] or as detailled report in data quality report format (*not implemented yet*).

## Table of Contents

- [Installation](#installation)
  - [From sources](#from-sources)
  - [With Docker](#with-docker)
- [Configuration](#configuration)
  - [Service settings](#service-settings)
  - [Profiles](#profiles)
  - [Checks](#checks)
- [API](#api)
  - [GET /{profile}/validate](#get-profilevalidate)
  - [POST /{profile}/validate](#get-profilevalidate)
  - [GET /profiles](#get-profiles)
  - [GET /reports/{id}](#get-reportid)
  - [DELETE /reports/{id}](#delete-reportid)
- [Library](#library)
- [Contributing](#contributing)
- [Maintainers](#maintainers)
- [License](#license)

## Installation

The web application is started on <http://localhost:7007> by default.

### From sources

Requires basic development toolchain (`sudo apt install build-essential`) and Python 3 with module venv to be installed.

1. clone repository: `git clone https://github.com/gbv/validation-api-ws.git && cd validation-api-ws`
2. run `make deps` to install dependencies
3. optionally [Configure](#configuration) the instance
3. `make start` 

### Via Docker

A Docker image is automatically build [and published](https://github.com/orgs/gbv/packages/container/package/validation-api-ws) on GitHub. To run a one-shot instance of the application from the most recent Docker image:

~~~sh
docker run --rm -p 7007:7007 ghcr.io/gbv/validation-api-ws:main
~~~

A [configuration](#configuration) directory or file must exist and be mounted:

~~~sh
test -f data/config.json && docker run --rm -p 7007:7007 --volume config:/app/config ghcr.io/gbv/validation-api-ws:main
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json ghcr.io/gbv/validation-api-ws:main
~~~

## Configuration

Create a configuration file `config.json` in the current directory or in the local subdirectory `config` to override the [default configuration](config.default.json). It is also possible to pass the location of config file or directory with argument `--config` at startup. The configuration file must contain field `profiles` with a list of [profiles](#profiles) and it can contain additional [service settings](#service-settings).

~~~json
{
  "port": 7007,
  "files": false,
  "reports": false,
  "downloads": false,
  "profiles": [
    {
      "id": "json",
      "url": "https://json.org/",
      "description": "Check data to be parseable JSON",
      "checks": ["json"]
    },
    {
      "id": "xml",
      "description": "Check data to be well-formed XML",
      "checks": ["xml"]
    }
  ]
}
~~~

### Service settings

- `title` (title of the service) is set to "Validation Service" by default.
- `port` (numeric port to run the service) is set to `7007` by default.
- `files` (stage directory for data files at the server) is set to `false` (disabled) by default.
- `reports` (reports directory to store reports in) is set to `false` (disabled) by default.
- `downloads` (cache directory for data retrieved via URL) is set to `false` (disabled) by default.

### Profiles

Each application profile is configured with a JSON object having a unique `id`, a list of `checks`, and additional metadata. See [profiles configuration JSON Schema](lib/validate/profiles-schema.json) for details of the configuration.

### Checks

Each check is either a string, referencing a base format or another profile, or a JSON object for a more complex check. By now only  [schema checks](#schema-checks) (against JSON Schema or XML Schema) have been implemented. Additional types of checks are planned.

#### Base formats

- `json` - validate JSON syntax
- `xml` - validate XML syntax (document must be well-formed XML)

#### Schema checks

Schema checks validates against a schema in some known schema language. The check is configured with two fields:

- `schema` - the schema language
- `location` - schema file or URL

The following schema languages are supported:

- `json-schema` - [JSON Schema](https://json-schema.org/)
- `xsd` - [XML Schema](https://www.w3.org/TR/xmlschema-0/)
- `schematron` [Schematron](https://en.wikipedia.org/wiki/Schematron)
- `avram` [Avram Schema](https://format.gbv.de/schema/avram/specification) *not implemented yet*
- `pcre` Regular Expression *not implemented yet*
- `shacl` [SHACL Shapes](https://www.w3.org/TR/shacl/) *not implemented yet*
- `antlr` [ANTLR](https://www.antlr.org/) Grammar *not implemented yet*

#### Script check

Script checks execute a script on the server (*not implemented yet*).

#### API call check

Pass data to another web service to be checked (*not implemented yet*).

#### Constraint check

Check data against complex constraints specified in AQinDa Constraint Language (*yet to be defined*)

## API

Details of **Data Validation API** are still being specified, so details may change. The core response format is being specified as **[Data Validation Report Format]**. This implementation provides one endpoint for each profile, accesible via both [GET](#get-profilevalidate) and [POST](#get-profilevalidate) requests. The additional endpoint to [list application profiles](#get-profiles) is not part of the core Data Validation API: other implementation might provide only one endpoint to validate againsta single application profile.

In addition there are optional endpoints [to look up](#get-reportsid) and [to remove](#delete-reportsid) validation reports.

### GET /{profile}/validate

Validate data against an application profile and return an error report in [Data Validation Report Format]. Data must be passed via one of these query parameters:

- `data` as string
- `url` to be downloaded from an URL (if the service is configured with `downloads` directory)
- `file` to be read from a local file in the stage directory of the server (if the service is configured with `files` directory)

Status code is always 200 if validation could be executed, no matter whether errors have been found or not. For example validating the string `[1,2` at default profile `json` results in the following validation response. The error position (after the fourth character on line 1) is referenced with multiple dimensions. Dimension values are always strings.

~~~sh
curl http://localhost:7007/json/validate -d '[1,2'
~~~

~~~json
{
  "errors": [
    {
      "message": "Expecting ',' delimiter",
      "position": {
        "line": "1",
        "linecol": "1:5",
        "offset": "4"
      }
    }
  ]
}
~~~

### POST /{profile}/validate

The validation endpoint can also be queried via HTTP POST: data can be passed as request body or as file upload (content type `multipart/form-data`). Additional query parameters are not supported.

### GET /profiles

Return a list of application profiles configured at this instance of the validation service. The information is a subset of [profiles configuration](#profiles) limited to the public fields `id` (required), `title`, `description`, `url`, and `report`. Internal information about checks is not included.

### GET /reports/{id}

Return a validation report. *This endpoint has not been specified nor implemented yet.*

### DELETE /reports/{id}

Delete a validation report. *This endpoint has not been specified nor implemented yet.*

## Library

The validation can also be used as Python library but its API has not stabilized yet. The implementation is build from the following components:

- `app.py` - a flask-based webservice
- class `ValidationService` - validation engine as service with reports and downloads.
- class `Validator` - validation engine
  - class `JSONSchemaValidator` - validate JSON against a JSON Schema
  - class `XSDValidator` - validate XML against an XML Schema
  - class `SchematronValidator` - validate XML against a Schematron Schema

## Contributing

- `make deps` installs Python dependencies in a virtual environment in directory `.venv`. You may also want to call `. .venv/bin/activate` to active the environment.
- `make test` runs unit tests
- `make all` runs unit tests and integration test. Also puts coverage report into directory `htmlcov`
- `make lint` checks coding style
- `make fix` cleans up some coding style violations
- `make loc` shows lines of code (requires `cloc` to be installed)

To locally build and run the image Docker for testing:

~~~sh
docker image build -t validator .
docker run --rm -p 7007:7007 validator  # default config, or:
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json validator
~~~

See also <https://github.com/gbv/validation-server> for a previous implementation in NodeJS. Both implementations may converge.

## Maintainers

- [@nichtich](https://github.com/nichtich)

## License

MIT © 2025- Verbundzentrale des GBV (VZG)

This work has been funded [by DFG in project *AQinDa*](https://gepris.dfg.de/gepris/projekt/521659096)

[Data Validation Report Format]: https://gbv.github.io/data-validation-report-format/
