# Installation

## Requirements

- Python **3.9+**
- OpenSSL libraries (provided by the `cryptography` package)
- A POSIX-like environment is recommended, but not required.

## From PyPI

```bash
pip install lupaxa-certtool
```

This installs:

- The Python package `lupaxa.certtool`
- The CLI entry point `certtool`

## Editable / Development Install

If you're working on the source:

```bash
git clone https://github.com/your-org/lupaxa-certtool.git
cd lupaxa-certtool

# Install with dev extras (ruff, mypy, pytest, bump2version, etc.)
pip install -e ".[dev]"
```

You can also use the provided Makefile shortcuts:

```bash
make install-dev   # editable install with dev extras
make install-test  # editable install with test extras only
```

## Verifying the Install

```bash
certtool --version
```

Or, via Python:

```python
from lupaxa.certtool import version

print(version())
```
