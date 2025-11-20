# Examples

This page shows practical command-line and Python examples for CertTool.

## 1. Generate a Single Cert from CLI

```bash
certtool \
  --common-name "dev.local" \
  --organization-name "The Lupaxa Project" \
  --digest-alg sha256 \
  --private-key-bits 4096 \
  --valid-days 730
```

This prints all three PEMs (cert, CSR, key) to stdout.

## 2. Generate with SANs via JSON

`configs/web-cert.json`:

```json
{
  "dn": {
    "commonName": "web.internal",
    "organizationName": "The Lupaxa Project"
  },
  "config": {
    "digest_alg": "sha512",
    "private_key_bits": 4096,
    "private_key_type": "RSA",
    "valid_days": 365,
    "encrypt_key": false
  },
  "subject_alt_names": [
    "web.internal",
    "api.internal",
    "10.0.0.10"
  ]
}
```

Command:

```bash
certtool --config configs/web-cert.json --output-dir certs/
```

Output:

```text
certs/web.internal/
  cert.pem
  csr.pem
  key.pem
```

## 3. Bulk Generation for Multiple Hosts

Layout:

```text
configs/
  db.json
  web.json
  cache.json
```

Command:

```bash
certtool --config-dir configs/ --output-dir certs/
```

This will produce:

```text
certs/
  db.internal/
    cert.pem
    csr.pem
    key.pem
  web.internal/
    cert.pem
    csr.pem
    key.pem
  cache.internal/
    cert.pem
    csr.pem
    key.pem
```

## 4. Programmatic Use from Python

```python
from pathlib import Path

from lupaxa.certtool import (
    CONFIG_DEFAULT,
    generate_from_dn_and_config,
    generate_from_json_file,
)

# Example 1: from JSON config
pem_bundle = generate_from_json_file(Path("configs/web-cert.json"))
print(pem_bundle.certificate_pem.decode("ascii"))

# Example 2: fully programmatic DN + CONFIG
dn = {
    "commonName": "prog.internal",
    "organizationName": "The Lupaxa Project",
}

cfg = dict(CONFIG_DEFAULT)
cfg["digest_alg"] = "sha256"
cfg["private_key_bits"] = 2048
cfg["valid_days"] = 90

pem_bundle2 = generate_from_dn_and_config(dn, cfg)
```

You can then write these PEMs to files, load them into other libraries, or feed them into test harnesses.
