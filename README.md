# Validation API (demo)

[![Docker image](https://github.com/gbv/validation-api-ws/actions/workflows/docker.yml/badge.svg)](https://github.com/orgs/gbv/packages/container/package/validation-api-ws)
[![Test](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml/badge.svg)](https://github.com/gbv/validation-api-ws/actions/workflows/test.yml)

> Demo of a simple Web API to validate data against predefined criteria

## Table of Contents

- [Usage](#usage)
  - [From sources](#from-sources)
  - [With Docker](#with-docker)
- [Configuration](#configuration)

## Usage

Start the the web application with default [configuration](#configuration) on port 7007.

### From sources

- Clone repository
- `make deps`
- `make start` 

### Via Docker

A Docker image is automatically build on GitHub.

Run from recent Docker image:

~~~sh
docker run --rm -p 7007:7007 ghcr.io/gbv/validation-api-ws:main
~~~

Same but with local config file (which must exist):

~~~sh
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/config.json ghcr.io/gbv/validation-api-ws:main
~~~

Run from locally built Docker image:

~~~sh
docker run --rm -p 7007:7007 validator
~~~

## Configuration

If local file `config.json` exist, it is used for configuration, otherwise [default configuration](config.default.json).

Configuration must contain key `profiles` with a list of profile objects, each having a unique `id` and a list of `checks`. See [profiles configuration JSON Schema](lib/validate/profiles-schema.json) for details. Additional config fields include:

- `title` (title of the webservice) is set to "Validation Service" by default.
- `port` (numeric port to run the webservice) is set to 7007 by default.
- `stage` (stage directory for data files at the server). Set to `false` (disabled) by default.
- `reports` (reports directory to store reports in). Set to `false` (disabled) by default.
- `downloads` (cache directory for data retrieved via URL). Set to `false` (disabled) by default.


## API


## Development

To locally build and run the image Docker for testing:

~~~sh
docker image build -t validator .
docker run --rm -p 7007:7007 validator  # default config, or:
test -f config.json && docker run --rm -p 7007:7007 --volume ./config.json:/app/configt.json validator
~~~

