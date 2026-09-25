# Getting Started

## Requirements

- Python **3.10+**
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
git clone https://github.com/lupaxa-security-toolbox/certtool.git
cd certtool

# Install with dev extras (ruff, mypy, pytest, bump-my-version, etc.)
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
