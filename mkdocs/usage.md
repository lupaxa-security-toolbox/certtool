# Usage

CertTool supports three main **generation modes**, plus two **utility modes**.

## Modes

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

**Using an output directory** (`--output-dir path/to/dir`):

- For each cert created, write to the `--output-dir` directory.

### Utility Modes

**Example config generation** (`--generate-example`):

- Prints an example JSON config to stdout, or writes it to `--example-file`.

**Config validation** (`--validate-config path/to/config.json`):

- Parses, merges with defaults, validates DN, key type, etc., and exits.

**Certificate inspection** (`--inspect-cert path/to/cert.pem`):

- Prints basic details (subject, issuer, SANs, validity) about a PEM certificate.

## Basic CLI Examples

### CLI-Only: Minimal DN on the Command Line

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

### Using a JSON Config File

```bash
certtool --config configs/dev-internal-cert.json
```

The JSON file can specify:

- `dn`: DN fields (e.g. `commonName`, `organizationName`, etc.)
- `config`: certificate options, such as `digest_alg`, `private_key_bits`, `valid_days`
- `subject_alt_names`: a list of SANs (DNS names and/or IP addresses)
- `passphrase`: optional passphrase for encrypting the private key

See [Configuration](#configuration) for details.

### Bulk Generation from a Directory

```bash
certtool --config-dir configs/ --output-dir output/
```

For each `*.json` file in `configs/`, this will:

- Generate a key, CSR, and certificate
- Place them under `output/<label>/` as `cert.pem`, `csr.pem`, `key.pem`
- `<label>` is derived from the `commonName` (preferred) or filename.

### Using an Output Directory

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

### Example Config Generation

```bash
certtool --generate-example
certtool --generate-example --example-file example-cert.json
```

### Validate Config Only

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

## Configuration

CertTool accepts configuration in JSON format for `--config` and `--config-dir` modes.

### Top-Level Shapes

Two main shapes are supported.

#### Explicit `dn` / `config` Blocks

```json
{
  "dn": {
    "countryName": "UK",
    "stateOrProvinceName": "Somerset",
    "localityName": "Glastonbury",
    "organizationName": "The Lupaxa Project",
    "organizationalUnitName": "Security Tools",
    "commonName": "dev.internal",
    "emailAddress": "not-a-real-email-address@thelupaxaproject.com"
  },
  "config": {
    "digest_alg": "sha512",
    "private_key_bits": 2048,
    "private_key_type": "RSA",
    "encrypt_key": false,
    "valid_days": 365
  },
  "subject_alt_names": [
    "dev.internal",
    "127.0.0.1"
  ],
  "passphrase": "EXAMPLE_ONLY_NOT_A_REAL_PASSWORD"
}
```

#### Flat Dictionary

```json
{
  "countryName": "UK",
  "commonName": "dev.internal",
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

### DN Fields

Supported DN keys:

- `countryName`
- `stateOrProvinceName`
- `localityName`
- `organizationName`
- `organizationalUnitName`
- `commonName` (required, non-empty)
- `emailAddress`

### Config Fields

The `config` block (or flat equivalents) can contain:

- `digest_alg` (string, one of `sha256`, `sha384`, `sha512`)
- `private_key_bits` (int, e.g. 2048, 4096)
- `private_key_type` (string, must be `"RSA"`)
- `encrypt_key` (bool, whether to encrypt the private key)
- `valid_days` (int, certificate validity period in days)

Encrypted keys use the passphrase from either:

- The JSON field `passphrase`, or
- The CLI `--passphrase` (which can override or supply it).

### Subject Alternative Names

SANs are supplied via `subject_alt_names`:

```json
{
  "subject_alt_names": [
    "dev.internal",
    "api.internal",
    "10.0.0.5"
  ]
}
```

Entries are validated as:

- DNS names (strings that are not valid IP addresses)
- IP addresses (v4/v6 where applicable)

These are embedded as a `SubjectAlternativeName` extension in the certificate.

### Passphrase Handling

Private key encryption can be enabled by:

- Setting `encrypt_key` to `true` in JSON or via CLI `--encrypt-key`
- Providing a `passphrase` in JSON or via CLI `--passphrase`

Precedence:

CLI `--passphrase` (if provided) → JSON `passphrase` → No passphrase (key is written unencrypted)

### Validating Configs

To sanity-check a config file:

```bash
certtool --validate-config configs/dev-internal-cert.json
```

This will error out if any of the following are invalid:

- Missing or empty `commonName`
- Unsupported `private_key_type`
- Non-integer `private_key_bits` or `valid_days`
- Invalid `encrypt_key` value

## Security

This project provides tools for generating and handling self-signed certificates.

These certificates are useful for local development, internal testing, and CI pipelines, but they must not be used in security-critical or public production environments.

### Self-Signed Certificates Are Not Trust Anchors

Self-signed certificates provide encryption only, not authentication.

They cannot be validated against a trusted Certificate Authority (CA), meaning:

- Any attacker can generate an identical self-signed certificate.
- Clients cannot verify the identity of the server.
- Users may be tricked into accepting fraudulent certificates.
- MITM (man-in-the-middle) attacks become trivial.

Never deploy self-signed certificates in production or on any externally reachable system.

They offer zero trust assurance and should only be used for:

- Local development
- Sandboxes
- CI environments
- Integration tests
- Temporary internal services behind additional layers of trust

### Private Key Handling and Storage

Regardless of certificate type, private keys must always be treated as highly sensitive.

Do:

- Store private keys with restrictive permissions (chmod 600).
- Keep keys outside source repositories.
- Ensure keys are excluded from backups when unnecessary.
- Rotate keys regularly.
- Prefer hardware-backed key storage when possible (TPM/HSM/YubiKey).

Do not:

- Commit private keys to Git repositories.
- Share keys via chat, email, or ticketing systems.
- Re-use keys across multiple certificates or servers.
- Leave keys on shared or untrusted machines.

Private key compromise completely undermines TLS security.

### Algorithm and Key Size Recommendations

This tool supports the following secure modern hashing algorithms:

- SHA-256
- SHA-384
- SHA-512

These are currently recommended for most use cases.

Avoid legacy algorithms such as SHA-1 or MD5, which are cryptographically broken.

Key size guidance:

- RSA 2048-bit minimum
- RSA 3072-bit recommended for long-term certificates
- RSA 4096-bit for high-security internal systems
- ECDSA (P-256 / P-384) is acceptable and efficient if supported by your environment

Avoid older curves (for example, P-192) and obscure or non-standard curves unless you fully understand the implications.

### Certificate Expiration and Rotation

Self-signed certificates should be:

- Short-lived (for example, 30–90 days for test environments)
- Rotated frequently
- Revoked immediately if the private key is compromised

Automated rotation through CI is strongly recommended.

> **Note:**
> Self-signed certificates do not support CRLs or OCSP, so revocation is effectively impossible once deployed.
> Rotation is the only real mitigation.

### TLS Configuration Best Practices

When deploying services using TLS (even with test certificates), ensure your server configuration follows modern guidance such as:

- Mozilla TLS Security Guidelines
- OWASP Transport Layer Protection Cheat Sheet
- NCSC TLS Configuration Guidelines

Key points include:

- Disable TLS 1.0 and TLS 1.1
- Prefer TLS 1.3 where possible
- Disable weak ciphers (3DES, RC4, CBC-only suites, EXPORT suites)
- Disable NULL and anonymous cipher suites
- Prefer modern AEAD ciphers (AES-GCM, CHACHA20-POLY1305)

TLS security is more than just the certificate.

### When to Use a Real Certificate Authority

Use CA-issued certificates when:

- The service is accessible to users or external systems
- Identity and trust must be verifiable
- The system is reachable beyond local development
- Compliance or regulatory requirements apply
- Long-term, stable environments are involved
- Services communicate over the public Internet

For internal private networks, a managed internal PKI or private CA is strongly preferred over ad-hoc self-signing.

### When This Tool is Appropriate

This tool is safe and appropriate for:

- Development environments
- CI/CD pipelines
- Automated integration tests
- Temporary internal experiments
- Local or ephemeral services
- Tools requiring short-lived encryption but not trust validation

It is not appropriate for anything requiring authenticated identity or long-term reliability.

### Additional Hardening Recommendations

- Use container isolation when generating keys/certs.
- Avoid using the same certificate for both client and server roles.
- Use separate keys for signing and encryption purposes.
- Ensure your build and deployment systems enforce strict secrets scanning.
- Automate scanning for expired or soon-to-expire certificates.

### Final Reminder

This project does not create trusted certificates.

It is intended to aid development workflows, not production security.

For real deployments:

- Use a proper CA
- Follow TLS best practices
- Protect private keys
- Validate and rotate certificates
- Use modern ciphers and enforce strict TLS configurations

Security failures are often due to operational mistakes rather than cryptographic ones. Treat certificates and keys with the same care as any critical secret.
