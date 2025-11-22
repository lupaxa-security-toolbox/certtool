<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/org-logos/master/orgs/security-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
  The Lupaxa Security Toolbox.<br />
  Part of The Lupaxa Project.
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
  --commonName "dev.internal"
```

## Using JSON Configuration

### Generate an example config

```bash
certtool --generate-example --example-file dev-internal-cert.json
```

### Use a JSON config file

```bash
certtool --config dev-internal-cert.json
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
├── dev.internal/
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
certtool --config dev-internal-cert.json --passphrase "some-secret"
```

## Inspect a Certificate

```bash
certtool --inspect-cert output/dev.interal/cert.pem
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

<footer>
    <h1>&nbsp;</h1>
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
</footer>
