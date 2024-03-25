# DB Kit

[![Build](https://github.com/SanctumLabs/dbkit/actions/workflows/build.yml/badge.svg)](https://github.com/SanctumLabs/dbkit/actions/workflows/build.yml)
[![Tests](https://github.com/SanctumLabs/dbkit/actions/workflows/tests.yaml/badge.svg)](https://github.com/SanctumLabs/dbkit/actions/workflows/tests.yaml)
[![Lint](https://github.com/SanctumLabs/dbkit/actions/workflows/lint.yml/badge.svg)](https://github.com/SanctumLabs/dbkit/actions/workflows/lint.yml)
[![Code Scanning](https://github.com/SanctumLabs/dbkit/actions/workflows/codeql.yaml/badge.svg)](https://github.com/SanctumLabs/dbkit/actions/workflows/codeql.yaml)

A wrapper for database packages which bakes in common database functionality.

## Pre-requisites

1. Ensure that you have [Python version 3.12.0](https://www.python.org/) setup locally, you can set this up
   using [pyenv](https://github.com/pyenv/pyenv) if you have multiple versions of Python on your local development
   environment.
2. [Poetry](https://python-poetry.org/) is used for managing dependencies, ensure you have that setup locally.
3. [Virtualenv](https://virtualenv.pypa.io/) Not a hard requirement as poetry should setup a virtual environment for
   you, but can be used as well to setup a virtual environment.

## Setup

1. After cloning the project, install the dependencies required with:

   ```shell
   poetry install
   ```
   > When using poetry

   Or
   ```shell
   make install
   ```
   > When using [GNU Make](https://www.gnu.org/s/make/manual/make.html), this is a wrapper around the top commend

## Installation

```bash
poetry add sanctumlabs_dbkit
```

## Features

* `on_commit` hooks for a when a transaction is committed.
* A DAO pattern for common methods such as `find`, `find_or_raise`, `all`...
* A `BaseModel` with baked in mixins for `timestamps`, `soft deletions`, `auditable` & more...
* Utility functions for working with models and schema.

See [usage examples here](docs/usage.py)
