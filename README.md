<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/org-logos/master/orgs/security-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
  The Lupaxa Security Toolbox.<br />
  Part of The Lupaxa Project.<br /><br />
  <!-- Core project badges -->
  <a href="https://github.com/lupaxa-security-toolbox/certtool/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/lupaxa-security-toolbox/certtool/ci.yml?branch=master&label=build%20status&style=for-the-badge" alt="Build Status"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/releases/latest">
    <img src="https://img.shields.io/github/v/release/lupaxa-security-toolbox/certtool?color=blue&label=Latest%20Release&style=for-the-badge" alt="Latest Release"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/releases">
    <img src="https://img.shields.io/github/release-date/lupaxa-security-toolbox/certtool?color=blue&label=Released&style=for-the-badge" alt="Release Date"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/master">
    <img src="https://img.shields.io/github/commits-since/lupaxa-security-toolbox/certtool/latest.svg?color=blue&style=for-the-badge" alt="Commits Since Release"/>
  </a>
  <br/>
  <!-- Community & ecosystem badges -->
  <a href="https://github.com/lupaxa-security-toolbox/certtool/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/lupaxa-security-toolbox/certtool?style=for-the-badge&color=blue" alt="Contributors"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/issues">
    <img src="https://img.shields.io/github/issues/lupaxa-security-toolbox/certtool?style=for-the-badge&color=blue" alt="Open Issues"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/pulls">
    <img src="https://img.shields.io/github/issues-pr/lupaxa-security-toolbox/certtool?style=for-the-badge&color=blue" alt="Open Pull Requests"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/certtool/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/lupaxa-security-toolbox/certtool?color=blue&label=License&style=for-the-badge" alt="License"/>
  </a>
  <br />
  <!-- Python (PyPI) -->
  <img src="https://img.shields.io/pypi/v/smartcache?style=for-the-badge&color=blue" alt="PyPI Version"/>
  <img src="https://img.shields.io/pypi/dm/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI downloads" />
  <img src="https://img.shields.io/pepy/dt/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI downloads" />
  <img src="https://img.shields.io/pypi/status/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI status" />
  <img src="https://img.shields.io/pypi/pyversions/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI supported python versions" />
</p>

# lupaxa-certtool

A clean, modern, fully-typed Python CLI and library for generating **self-signed X.509 certificates**, **certificate signing requests (CSRs)**, and **private keys**.

Built for automation, reproducibility, and bulk-generation workflows used by The Lupaxa Project.

## Features

- Generate **self-signed certificates**, **private keys**, and **CSRs**
- Generate from:
  - **JSON config file**
  - **Directory of config files** (bulk mode)
  - **Pure command-line flags**
- Output:
  - To **stdout**
  - Or into an **output directory**, with one folder per certificate
- Supports:
  - RSA key generation
  - SHA-256 / SHA-384 / SHA-512 digests
  - Validity period configuration
  - Optional **private key encryption** with passphrase
  - **Subject Alternative Names (SANs)** via JSON or CLI
- Includes:
  - `--generate-example` to produce a full example JSON config
  - `--inspect-cert` to analyze existing PEM certificates
  - `--validate-config` to validate config files before use
- Fully typed, linted, formatted, and tested
- MkDocs documentation included

## Installation

### From PyPI

```bash
pip install lupaxa-certtool
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

## Usage

### Basic self-signed certificate from CLI

```bash
certtool \
  --countryName UK \
  --stateOrProvinceName Somerset \
  --localityName Glastonbury \
  --organizationName "Lupaxa Project" \
  --commonName "example.local"
  ```

## Using JSON Configuration

### Generate an example config

```bash
certtool --generate-example --example-file example-cert.json
```

### Use a JSON config file

```bash
certtool --config example-cert.json
```

### Use a directory of configs (bulk mode)

```bash
certtool --config-dir configs/
```

## Output Directory Structure

If you pass:

```bash
certtool --config-dir configs/ --output-dir output/
```

You get:

```bash
output/
├── example.local/
│   ├── cert.pem
│   ├── csr.pem
│   └── key.pem
└── api.internal/
    ├── cert.pem
    ├── csr.pem
    └── key.pem
```

Each certificate gets its own folder to prevent overwriting.

## Private Key Encryption

### JSON

```bash
{
  "passphrase": "your-secret-here"
}
```

### CLI (overrides JSON)

```bash
certtool --config server.json --passphrase "some-secret"
```

## Inspect a Certificate

```bash
certtool --inspect-cert output/example.local/cert.pem
```

## Development

### Run tests

```bash
make test
```

### Type checking

```bash
make type
```

### Lint, format, and style checks

```bash
make check-style
```

### Run everything

```bash
make check-all
```

### Build documentation

```bash
mkdocs serve
```

## Documentation

The project includes MkDocs documentation.

### Online documentation:

[Documentation](https://lupaxa-security-toolbox.github.io/certtool/)

Full documentation is available in the docs/ directory or served locally:

### Serve docs locally

```bash
mkdocs serve
```

Then open the printed URL (usually http://127.0.0.1:8000/) in your browser.

## Development

Clone the repository and install dev dependencies:

```bash
pip install -e ".[dev]"
```

Useful make targets:

```bash
make test        # run tests
make type        # type checking (mypy)
make check-style # lint + format + type
make check-all   # run tests, coverage, and audit
```

## Repository Layout

```bash
lupaxa-certtool/
├── src/lupaxa/certtool/
│   ├── cli.py
│   ├── certs.py
│   ├── utils.py
│   ├── config.py
│   ├── example.py
│   ├── exceptions.py
│   ├── version.py
│   └── __init__.py
├── docs/
├── tests/
├── mkdocs.yml
├── Makefile
├── pyproject.toml
├── .editorconfig
├── .gitignore
└── README.md
```
<h1></h1>

<p align="center">
    <strong>
        &copy; The Lupaxa Project.
    </strong>
    <br />
    <em>
        Where exploration meets precision.<br />
        Where the untamed meets the engineered.
    </em>
</p>

