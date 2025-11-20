# Lupaxa CertTool

`lupaxa-certtool` is a small, security-focused utility for generating **self-signed X.509 certificates**, 
**certificate signing requests (CSRs)**, and **private keys** from either:

- Command-line options (DN + config), or  
- One or more JSON configuration files.

It is designed for:

- Local development
- Labs, demos and PoCs
- Quickly bootstrapping TLS for services like Apache, Nginx, or internal tools

## Features

- 🧾 CLI and Python API
- 🧬 JSON-based configuration (single file or directory of files)
- 📂 Optional output directory with per-certificate subdirectories
- 🔑 RSA key generation (configurable key size)
- 📜 Self-signed certificates with configurable validity
- 📨 SAN (Subject Alternative Name) support via JSON
- 🧪 Built-in `--validate-config` to check JSON configs
- 🔍 `--inspect-cert` to inspect existing PEM certificates
- 🧪 Fully tested with `pytest`, `ruff`, and `mypy`

## Project Layout

```text
src/lupaxa/certtool/
  __init__.py
  certs.py
  cli.py
  config.py
  example.py
  exceptions.py
  utils.py
  version.py
```

For full details, see:

- [Installation](installation.md)
- [Usage](usage.md)
- [Configuration](configuration.md)
- [CLI Reference](cli.md)
- [Examples](examples.md)
- [API Reference](reference/certs.md)
