# Security Guidance

This project provides tools for generating and handling self-signed certificates.

These certificates are useful for local development, internal testing, and CI pipelines, but they must not be used in security-critical
or public production environments.

The guidance on this page outlines the security considerations, limitations, and recommended best practices when using this tool.

## Self-Signed Certificates Are Not Trust Anchors

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

## Private Key Handling & Storage

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

## Algorithm & Key Size Recommendations

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

Avoid older curves (e.g., P-192) and obscure or non-standard curves unless you fully understand the implications.

## Certificate Expiration & Rotation

Self-signed certificates should be:

- Short-lived (e.g., 30–90 days for test environments)
- Rotated frequently
- Revoked immediately if the private key is compromised

Automated rotation through CI is strongly recommended.

> Note:
> Self-signed certificates do not support CRLs or OCSP, so revocation is effectively impossible once deployed.
> Rotation is the only real mitigation.

## TLS Configuration Best Practices

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

## When to Use a Real Certificate Authority (CA)

Use CA-issued certificates when:

- The service is accessible to users or external systems
- Identity and trust must be verifiable
- The system is reachable beyond local development
- Compliance or regulatory requirements apply
- Long-term, stable environments are involved
- Services communicate over the public Internet

For internal private networks, a managed internal PKI or private CA is strongly preferred over ad-hoc self-signing.

## When This Tool Is Appropriate

This tool is safe and appropriate for:

- Development environments
- CI/CD pipelines
- Automated integration tests
- Temporary internal experiments
- Local or ephemeral services
- Tools requiring short-lived encryption but not trust validation

It is not appropriate for anything requiring authenticated identity or long-term reliability.

## Additional Hardening Recommendations

- Use container isolation when generating keys/certs.
- Avoid using the same certificate for both client and server roles.
- Use separate keys for signing and encryption purposes.
- Ensure your build and deployment systems enforce strict secrets scanning.
- Automate scanning for expired or soon-to-expire certificates.

## Final Reminder

This project does not create trusted certificates.

It is intended to aid development workflows, not production security.

For real deployments:

- Use a proper CA
- Follow TLS best practices
- Protect private keys
- Validate and rotate certificates
- Use modern ciphers and enforce strict TLS configurations

Security failures are often due to operational mistakes rather than cryptographic ones—treat certificates and keys with the same
care as any critical secret.
