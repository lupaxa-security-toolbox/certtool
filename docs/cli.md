# CLI Reference

The `certtool` CLI is installed with the `lupaxa-certtool` package.

## Basic Syntax

```bash
certtool [MODE OPTIONS] [DN OPTIONS] [CONFIG OPTIONS]
```

## Modes

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
certtool --generate-example --example-file example-cert.json
```

- Without `--example-file`, prints JSON to stdout.
- With `--example-file`, writes JSON to that file.
- Must not be combined with any certificate-generation options.

### `--validate-config PATH`

```bash
certtool --validate-config configs/example-cert.json
```

- Loads the JSON
- Merges with defaults
- Validates DN and configuration
- Prints a success message or raises an error

### `--inspect-cert PATH`

```bash
certtool --inspect-cert certs/dev.local/cert.pem
```

Prints basic information about an existing PEM certificate, including:

- Subject
- Issuer
- Validity period
- Subject Alternative Names (if present)

### `--config PATH`

Use a single JSON configuration file:

```bash
certtool --config configs/example-cert.json --output-dir certs/
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
certtool --config configs/example-cert.json --output-dir certs/
```

If omitted, PEMs are printed to stdout.  
If provided, PEMs go into a per-cert subdirectory under `PATH`.

### `--passphrase VALUE`

```bash
certtool --config configs/example-cert.json --encrypt-key --passphrase "EXAMPLE_ONLY_NOT_A_REAL_PASSWORD"
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
  --common-name "dev.local" \
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
  --common-name "dev.local" \
  --digest-alg sha256 \
  --private-key-bits 4096 \
  --valid-days 365 \
  --no-encrypt-key
```
