# Reference

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

## Mode Options

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

## DN Options

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

## Config Options

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

## CLI Module

`lupaxa.certtool.cli` is the CLI integration and top-level controller.

### Key Functions

- `parse_args() -> argparse.Namespace` — build the `argparse` parser with all CLI options.
- `validate_mode_constraints(args)` — enforce mutual exclusivity between modes and ensure consistent use of `--config`, `--config-dir`, `--generate-example`, and the other mode flags.
- `process_config_dir_mode(config_dir, output_dir, passphrase)` — iterate over all JSON configs in a directory and generate certificates.
- `process_config_file_mode(config_file, output_dir, passphrase)` — process a single JSON config file.
- `process_cli_mode(args, output_dir)` — CLI-only mode: merge DN + CONFIG from arguments and generate.
- `run(args: argparse.Namespace) -> None` — high-level controller used by both tests and `main()`.
- `main() -> None` — entry point for the `certtool` console script.

### Modes Implemented

- `--version`
- `--generate-example` / `--example-file`
- `--validate-config`
- `--inspect-cert`
- `--config` / `--config-dir`
- DN and CONFIG CLI options

## Configuration Module

`lupaxa.certtool.config` loads and validates configuration.

### Key Functions

- `load_json_config(path: Path) -> tuple[dict[str, object], dict[str, object]]` — load DN/CONFIG from a JSON file. Supports an explicit `{"dn": {...}, "config": {...}}` object and a flat dictionary, where keys are split between DN and CONFIG.
- `validate_dn(dn: dict[str, object]) -> None` — ensure that DN is usable. Requires at least a non-empty `commonName`. Raises `ConfigError` on invalid DN.
- `merge_settings_cli(args) -> tuple[dict[str, object], dict[str, object]]` — CLI-only mode: derive DN and CONFIG from CLI arguments and defaults.
- `merge_settings_json(json_dn, json_cfg) -> tuple[dict[str, object], dict[str, object]]` — JSON-based modes: merge JSON DN/CONFIG with defaults and validate.

## Certificate Generation

`lupaxa.certtool.certs` contains the cryptographic primitives and high-level generation API.

### Responsibilities

- Constructing X.509 subject names from DN dicts.
- Generating RSA private keys.
- Creating CSRs and self-signed certificates.
- Serializing artifacts into PEM bundles.
- Providing convenience APIs for generating from JSON configs or in-memory configuration.

### Key Classes

#### `CertComponents`

Container for in-memory certificate-related objects:

- `private_key`: `rsa.RSAPrivateKey`
- `csr`: `x509.CertificateSigningRequest`
- `cert`: `x509.Certificate`

#### `PemBundle`

Serialized PEM artifacts:

- `certificate_pem`: bytes
- `csr_pem`: bytes
- `private_key_pem`: bytes

### Key Functions

- `build_x509_name(dn: dict[str, str]) -> x509.Name` — build a subject name from a DN dict.
- `generate_key_pair(bits: int) -> rsa.RSAPrivateKey` — create an RSA private key.
- `generate_csr(private_key, subject, digest_alg) -> x509.CertificateSigningRequest` — build and sign a CSR.
- `generate_self_signed_cert(private_key, subject, digest_alg, valid_days) -> x509.Certificate` — generate a self-signed X.509 certificate.
- `create_cert_components(dn, cfg) -> CertComponents` — generate key, CSR, and cert in one call.
- `serialize_cert_components(components, encrypt_key: bool) -> PemBundle` — serialize components into PEM-encoded bytes.
- `handle_single_cert(dn, cfg, label, output_dir)` — run the full pipeline (generate, serialize, write to stdout or disk).
- `generate_from_json_file(path: Path) -> PemBundle` — load JSON config, merge, validate, and return a `PemBundle`.
- `generate_from_dn_and_config(dn, cfg) -> PemBundle` — programmatic generation without JSON.

## Example Helpers

`lupaxa.certtool.example` builds example configuration files.

### Key Functions

- `build_example_config() -> dict[str, object]` — build an in-memory example JSON configuration structure which includes a realistic DN, reasonable config defaults, sample `subject_alt_names`, and an example `passphrase`.
- `generate_example_config(example_file: Path | None) -> None` — write the example JSON configuration either to stdout (if `example_file` is `None`) or to the specified file, creating parent directories as needed.

## Exceptions

`lupaxa.certtool.exceptions` is the custom exception hierarchy.

### Base Class

- `CertToolError(Exception)` — all tool-specific exceptions derive from this base.

### Subclasses

- `ConfigError(CertToolError)` — raised when CLI or JSON configuration is invalid, inconsistent, or missing required fields (for example `commonName`).
- `GenerationError(CertToolError)` — raised when cryptographic operations fail, such as key generation, CSR creation, certificate signing, or serialization.
- `OutputError(CertToolError)` — raised when output directories or files cannot be created or written.

## Utilities

`lupaxa.certtool.utils` holds shared constants and helpers.

### Constants

- `DN_KEYS: list[str]` — ordered list of supported DN keys: `countryName`, `stateOrProvinceName`, `localityName`, `organizationName`, `organizationalUnitName`, `commonName`, `emailAddress`.
- `CONFIG_DEFAULT: dict[str, object]` — default configuration dictionary: `digest_alg` `"sha512"`, `private_key_bits` `2048`, `private_key_type` `"RSA"`, `encrypt_key` `False`, `valid_days` `365`.

### Functions

- `slugify(value: str) -> str` — convert an arbitrary string into a filesystem-safe slug.
- `make_cert_subdir(base_output_dir, dn, label) -> Path` — create a unique subdirectory for a certificate set based on `commonName` (preferred), then `label` (for example the config filename stem), then a fallback of `"cert"` with numeric suffixes.
- `prepare_output_dir(path: Path | None) -> Path | None` — ensure the output directory exists (if one is requested).

## Version

`lupaxa.certtool.version` exposes the package version.

### Functions

- `get_version() -> str` — return the current version string embedded in `__version__`.

The package also exposes `version()` via the public API:

```python
from lupaxa.certtool import version

print(version())
```
