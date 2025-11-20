<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/org-logos/master/orgs/security-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
  <!-- Core project badges -->
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/lupaxa-security-toolbox/self-signed-certificates/ci.yml?branch=master&label=build%20status&style=for-the-badge" alt="Build Status"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/releases/latest">
    <img src="https://img.shields.io/github/v/release/lupaxa-security-toolbox/self-signed-certificates?color=blue&label=Latest%20Release&style=for-the-badge" alt="Latest Release"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/releases">
    <img src="https://img.shields.io/github/release-date/lupaxa-security-toolbox/self-signed-certificates?color=blue&label=Released&style=for-the-badge" alt="Release Date"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/master">
    <img src="https://img.shields.io/github/commits-since/lupaxa-security-toolbox/self-signed-certificates/latest.svg?color=blue&style=for-the-badge" alt="Commits Since Release"/>
  </a>
  <br/>
  <!-- Community & ecosystem badges -->
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/lupaxa-security-toolbox/self-signed-certificates?style=for-the-badge&color=blue" alt="Contributors"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/issues">
    <img src="https://img.shields.io/github/issues/lupaxa-security-toolbox/self-signed-certificates?style=for-the-badge&color=blue" alt="Open Issues"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/pulls">
    <img src="https://img.shields.io/github/issues-pr/lupaxa-security-toolbox/self-signed-certificates?style=for-the-badge&color=blue" alt="Open Pull Requests"/>
  </a>
  <a href="https://github.com/lupaxa-security-toolbox/self-signed-certificates/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/lupaxa-security-toolbox/self-signed-certificates?color=blue&label=License&style=for-the-badge" alt="License"/>
  </a>
  <br />
  <!-- Python (PyPI) -->
  <a href="https://pypi.org/project/smartcache/">
    <img src="https://img.shields.io/pypi/v/smartcache?style=for-the-badge&color=blue" alt="PyPI Version"/>
  </a>
  <a href="#">
    <img src="https://img.shields.io/pypi/dm/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI downloads" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/pepy/dt/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI downloads" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/pypi/status/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI status" />
  </a>
  <a href="#">
    <img src="https://img.shields.io/pypi/pyversions/lupaxa-certtool?style=for-the-badge&color=blue" alt="PyPI supported python versions" />
  </a>
</p>

# lupaxa-certtool

A clean, modern, fully-typed Python CLI and library for generating **self-signed X.509 certificates**, **certificate signing requests (CSRs)**, and **private keys**.

Built for automation, reproducibility, and bulk-generation workflows used by The Lupaxa Project.

## ✨ Features

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

Full documentation is available in the docs/ directory or served locally:

```bash
mkdocs serve
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

