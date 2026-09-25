<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">CertTool</h1>

A clean, modern, fully-typed Python CLI and library for generating **self-signed X.509 certificates**, **certificate signing requests (CSRs)**, and **private keys**.

Built for automation, reproducibility, and bulk-generation workflows used by The Lupaxa Project.

## Features

-   Generate **self-signed certificates**, **private keys**, and **CSRs**
-   Generate from:
    - **JSON config file**
    - **Directory of config files** (bulk mode)
    - **Pure command-line flags**
-   Output:
    - To **stdout**
    - Or into an **output directory**, with one folder per certificate
-   Supports:
    - RSA key generation
    - SHA-256 / SHA-384 / SHA-512 digests
    - Validity period configuration
    - Optional **private key encryption** with passphrase
    - **Subject Alternative Names (SANs)** via JSON or CLI
-   Includes:
    - `--generate-example` to produce a full example JSON config
    - `--inspect-cert` to analyze existing PEM certificates
    - `--validate-config` to validate config files before use
-   Fully typed, linted, formatted, and tested
-   MkDocs documentation included

## Installation

### From PyPI

```bash
pip install lupaxa-certtool
```

### From Source (Development Mode)

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Self-Signed Certificate from CLI

```bash
certtool \
  --countryName UK \
  --stateOrProvinceName Somerset \
  --localityName Glastonbury \
  --organizationName "Lupaxa Project" \
  --commonName "dev.internal"
```

## Using JSON Configuration

### Generate an Example Config

```bash
certtool --generate-example --example-file dev-internal-cert.json
```

### Use a JSON Config File

```bash
certtool --config dev-internal-cert.json
```

### Use a Directory of Configs (Bulk Mode)

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

### CLI (Overrides JSON)

```bash
certtool --config dev-internal-cert.json --passphrase "some-secret"
```

## Inspect a Certificate

```bash
certtool --inspect-cert output/dev.interal/cert.pem
```

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

## Documentation

The published guide is at
<https://certtool.thelupaxaproject.org/>.

Site Markdown lives in `mkdocs/`.

```bash
python -m pip install -r requirements.txt
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
