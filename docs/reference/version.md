# `lupaxa.certtool.version`

Version information helpers.

## Functions

- `get_version() -> str`  
  Return the current version string embedded in `__version__`.

The package also exposes `version()` via the public API:

```python
from lupaxa.certtool import version

print(version())
```
