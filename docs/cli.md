# CLI Reference

The `certtool` CLI is installed with the `lupaxa-certtool` package.

## Basic Syntax

```bash
certtool [MODE OPTIONS] [DN OPTIONS] [CONFIG OPTIONS]
```

## All Options

```bash
  -h, --help            show this help message and exit
  -V, --version         Show program version and exit.
  --generate-example    Generate an example JSON configuration and exit.
  --example-file EXAMPLE_FILE
                        When used with --generate-example, write the example JSON configuration to this file instead of stdout.
  --config CONFIG       Path to JSON config file for DN and certificate settings.
  --config-dir CONFIG_DIR
                        Directory containing JSON config files for bulk generation.
  --output-dir OUTPUT_DIR
                        Directory to write outputs into. For each cert, a subdirectory will be created containing cert.pem, csr.pem, key.pem.
  --validate-config FILE
                        Validate a JSON configuration file and exit without generating certificates.
  --inspect-cert CERT   Inspect an existing PEM-encoded certificate and print basic details.
  --country-name COUNTRYNAME
                        Country Name (C). Example: UK
  --state-or-province-name STATEORPROVINCENAME
                        State or Province Name (ST). Example: Somerset
  --locality-name LOCALITYNAME
                        Locality Name (L). Example: Glastonbury
  --organization-name ORGANIZATIONNAME
                        Organization Name (O).
  --organizational-unit-name ORGANIZATIONALUNITNAME
                        Organizational Unit Name (OU).
  --common-name COMMONNAME
                        Common Name (CN). For SSL: hostname; for S/MIME: person's name.
  --email-address EMAILADDRESS
                        Email Address.
  --digest-alg {sha512,sha384,sha256}
                        Digest algorithm to use for signing. Default: sha512
  --private-key-bits PRIVATE_KEY_BITS
                        Private key size in bits. Default: 2048
  --private-key-type PRIVATE_KEY_TYPE
                        Private key type (currently only RSA is supported).
  --valid-days VALID_DAYS
                        Validity period for the certificate in days. Default: 365
  --encrypt-key         Encrypt private key with a passphrase (placeholder in code).
  --no-encrypt-key      Do not encrypt private key (default).
  --passphrase PASSPHRASE
                        Passphrase to use when encrypting the private key (if --encrypt-key is set).
```

## Mode Options (CLI-Only Options)

These options are mutually constrained:

- `--config PATH`
- `--config-dir PATH`
- `--generate-example`
- `--validate-config PATH`
- `--inspect-cert PATH`
- `--version`

### `--version`

```bash
certtool --version
```

Prints the current version string and exits.

### `--generate-example`

```bash
certtool --generate-example
certtool --generate-example --example-file dev-internal-cert.json
```

- Without `--example-file`, prints JSON to stdout.
- With `--example-file`, writes JSON to that file.
- Must not be combined with any certificate-generation options.

### `--validate-config PATH`

```bash
certtool --validate-config configs/dev-internal-cert.json
```

- Loads the JSON
- Merges with defaults
- Validates DN and configuration
- Prints a success message or raises an error

### `--inspect-cert PATH`

```bash
certtool --inspect-cert certs/dev.internal/cert.pem
```

Prints basic information about an existing PEM certificate, including:

- Subject
- Issuer
- Validity period
- Subject Alternative Names (if present)

### `--config PATH`

Use a single JSON configuration file:

```bash
certtool --config configs/dev-internal-cert.json --output-dir certs/
```

DN/CONFIG CLI flags are not allowed in this mode.

### `--config-dir PATH`

Use a directory of JSON configuration files:

```bash
certtool --config-dir configs/ --output-dir certs/
```

For each `*.json` in the directory, a separate cert set is generated.

### `--output-dir PATH`

```bash
certtool --config configs/dev-internal-cert.json --output-dir certs/
```

If omitted, PEMs are printed to stdout.
If provided, PEMs go into a per-cert subdirectory under `PATH`.

### `--passphrase VALUE`

```bash
certtool --config configs/dev-internal-cert.json --encrypt-key --passphrase "EXAMPLE_ONLY_NOT_A_REAL_PASSWORD"
```

- Used only if `encrypt_key` is true in config (JSON or CLI).
- Overrides `passphrase` in JSON if both are present.

## DN Options (CLI-Only Mode)

Only valid when **not** using `--config` or `--config-dir`.

- `--country-name`
- `--state-or-province-name`
- `--locality-name`
- `--organization-name`
- `--organizational-unit-name`
- `--common-name`
- `--email-address`

Example:

```bash
certtool \
  --common-name "dev.internal" \
  --organization-name "The Lupaxa Project"
```

## Config Options (CLI-Only Mode)

Only valid when **not** using `--config` / `--config-dir`:

- `--digest-alg` (`sha256`, `sha384`, `sha512`)
- `--private-key-bits` (e.g. 2048, 4096)
- `--private-key-type` (currently only `"RSA"`)
- `--valid-days` (e.g. 365)
- `--encrypt-key` / `--no-encrypt-key`

Example:

```bash
certtool \
  --common-name "dev.internal" \
  --digest-alg sha256 \
  --private-key-bits 4096 \
  --valid-days 365 \
  --no-encrypt-key
```
