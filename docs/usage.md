# Usage

CertTool supports three main **generation modes**, plus two **utility modes**.

## Modes Overview

### Generation Modes

**CLI-only mode** (no `--config` / `--config-dir`):

- DN (Distinguished Name) comes solely from CLI options.
- Config options are taken from defaults, then overridden by CLI flags.
- No DN defaults: `commonName` **must** be provided.

**Config file mode** (`--config path/to/file.json`):

- DN and CONFIG come from the JSON file.
- DN/CONFIG CLI options are **not allowed** in this mode.

**Config directory mode** (`--config-dir path/to/dir/`):

- For each `*.json` in the directory, DN and CONFIG come from that file.
- DN/CONFIG CLI options are **not allowed**.
- Perfect for bulk generation.

**Using an Output Directory** (`--output-dir path/to/dir`):

- For each cert created, write to the `--output-dir` directory.

### Utility Modes

**Example config generation** (`--generate-example`):

- Prints an example JSON config to stdout, or writes it to `--example-file`.

**Config validation** (`--validate-config path/to/config.json`):

- Parses, merges with defaults, validates DN, key type, etc., and exits.

**Certificate inspection** (`--inspect-cert path/to/cert.pem`):

- Prints basic details (subject, issuer, SANs, validity) about a PEM certificate.

## Basic CLI Examples

### Generation Modes

#### CLI-Only: Minimal DN on the command line

```bash
certtool \
  --common-name "dev.internal" \
  --organization-name "The Lupaxa Project"
```

This will:

- Generate an RSA private key (2048 bits by default)
- Create a CSR with the provided DN
- Create a self-signed certificate (valid for 365 days)
- Print the cert, CSR, and key to stdout in PEM format.

#### Using a JSON Config File

```bash
certtool --config configs/dev-internal-cert.json
```

The JSON file can specify:

- `dn`: DN fields (e.g. `commonName`, `organizationName`, etc.)
- `config`: certificate options, such as `digest_alg`, `private_key_bits`, `valid_days`
- `subject_alt_names`: a list of SANs (DNS names and/or IP addresses)
- `passphrase`: optional passphrase for encrypting the private key

See [Configuration](configuration.md) for details.

#### Bulk Generation from a Directory

```bash
certtool --config-dir configs/ --output-dir output/
```

For each `*.json` file in `configs/`, this will:

- Generate a key, CSR, and certificate
- Place them under `output/<label>/` as `cert.pem`, `csr.pem`, `key.pem`
- `<label>` is derived from the `commonName` (preferred) or filename.

#### Using an Output Directory

By default, PEMs are printed to stdout. To write to disk:

```bash
certtool --config configs/dev-internal-cert.json --output-dir certs/
```

Output will be created under:

```text
certs/
  dev.internal/
    cert.pem
    csr.pem
    key.pem
```

### Utility Modes

#### Example Config Generation

```bash
certtool --generate-example
certtool --generate-example --example-file example-cert.json
```

#### Validate Config Only

```bash
certtool --validate-config configs/dev-internal-cert.json
```

This will:

- Parse the JSON
- Merge with defaults
- Check the DN (requires `commonName`)
- Check `private_key_type` is supported (`RSA`)
- Report success or raise an error

### Inspect an Existing Certificate

```bash
certtool --inspect-cert certs/dev-internal-cert/cert.pem
```

This prints:

- Subject
- Issuer
- Not Before / Not After
- Subject Alternative Names (if present)
