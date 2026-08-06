# `lupaxa.certtool.certs`

This module contains the cryptographic primitives and high-level
generation API.

## Responsibilities

- Constructing X.509 subject names from DN dicts.
- Generating RSA private keys.
- Creating CSRs and self-signed certificates.
- Serializing artifacts into PEM bundles.
- Providing convenience APIs for generating from JSON configs or
  in-memory configuration.

## Key Classes

### `CertComponents`

Container for in-memory certificate-related objects:

- `private_key`: `rsa.RSAPrivateKey`
- `csr`: `x509.CertificateSigningRequest`
- `cert`: `x509.Certificate`

### `PemBundle`

Serialized PEM artifacts:

- `certificate_pem`: bytes
- `csr_pem`: bytes
- `private_key_pem`: bytes

## Key Functions

- `build_x509_name(dn: dict[str, str]) -> x509.Name`  
  Build a subject name from a DN dict.

- `generate_key_pair(bits: int) -> rsa.RSAPrivateKey`  
  Create an RSA private key.

- `generate_csr(private_key, subject, digest_alg) -> x509.CertificateSigningRequest`  
  Build and sign a CSR.

- `generate_self_signed_cert(private_key, subject, digest_alg, valid_days) -> x509.Certificate`  
  Generate a self-signed X.509 certificate.

- `create_cert_components(dn, cfg) -> CertComponents`  
  Generate key, CSR, and cert in one call.

- `serialize_cert_components(components, encrypt_key: bool) -> PemBundle`  
  Serialize components into PEM-encoded bytes.

- `handle_single_cert(dn, cfg, label, output_dir)`  
  Run the full pipeline (generate, serialize, write to stdout or disk).

- `generate_from_json_file(path: Path) -> PemBundle`  
  Load JSON config, merge, validate, and return a `PemBundle`.

- `generate_from_dn_and_config(dn, cfg) -> PemBundle`  
  Purely programmatic generation without JSON.
