# Configuration

CertTool accepts configuration in JSON format for `--config` and `--config-dir` modes.

## Top-Level Shapes

Two main shapes are supported:

### 1. Explicit `dn` / `config` Blocks

```json
{
  "dn": {
    "countryName": "UK",
    "stateOrProvinceName": "Somerset",
    "localityName": "Glastonbury",
    "organizationName": "The Lupaxa Project",
    "organizationalUnitName": "Security Tools",
    "commonName": "dev.local",
    "emailAddress": "admin@example.com"
  },
  "config": {
    "digest_alg": "sha512",
    "private_key_bits": 2048,
    "private_key_type": "RSA",
    "encrypt_key": false,
    "valid_days": 365
  },
  "subject_alt_names": [
    "dev.local",
    "127.0.0.1"
  ],
  "passphrase": "EXAMPLE_ONLY_NOT_A_REAL_PASSWORD"
}
```

### 2. Flat Dictionary

```json
{
  "countryName": "UK",
  "commonName": "dev.local",
  "digest_alg": "sha512",
  "private_key_bits": 2048,
  "private_key_type": "RSA",
  "valid_days": 365
}
```

In this form:

- Keys matching DN fields go into `dn`
- Keys matching CONFIG fields go into `config`
- Unknown keys are ignored (except `subject_alt_names` and `passphrase`, which are handled explicitly).

## DN Fields

Supported DN keys:

- `countryName`
- `stateOrProvinceName`
- `localityName`
- `organizationName`
- `organizationalUnitName`
- `commonName` (required, non-empty)
- `emailAddress`

## Config Fields

The `config` block (or flat equivalents) can contain:

- `digest_alg` (string, one of `sha256`, `sha384`, `sha512`)
- `private_key_bits` (int, e.g. 2048, 4096)
- `private_key_type` (string, must be `"RSA"`)
- `encrypt_key` (bool, whether to encrypt the private key)
- `valid_days` (int, certificate validity period in days)

Encrypted keys use the passphrase from either:

- The JSON field `passphrase`, or
- The CLI `--passphrase` (which can override or supply it).

## Subject Alternative Names (SAN)

SANs are supplied via `subject_alt_names`:

```json
{
  "subject_alt_names": [
    "dev.local",
    "api.local",
    "10.0.0.5"
  ]
}
```

Entries are validated as:

- DNS names (strings that are not valid IP addresses)
- IP addresses (v4/v6 where applicable)

These are embedded as a `SubjectAlternativeName` extension in the certificate.

## Passphrase Handling

Private key encryption can be enabled by:

- Setting `encrypt_key` to `true` in JSON or via CLI `--encrypt-key`
- Providing a `passphrase` in JSON or via CLI `--passphrase`

Precedence:

1. CLI `--passphrase` (if provided)
2. JSON `passphrase`
3. No passphrase → key is written unencrypted.

## Validating Configs

To sanity-check a config file:

```bash
certtool --validate-config configs/example-cert.json
```

This will error out if any of the following are invalid:

- Missing or empty `commonName`
- Unsupported `private_key_type`
- Non-integer `private_key_bits` or `valid_days`
- Invalid `encrypt_key` value
