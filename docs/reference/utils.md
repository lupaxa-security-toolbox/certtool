# `lupaxa.certtool.utils`

Utility helpers and shared constants.

## Constants

- `DN_KEYS: list[str]`  
  Ordered list of supported DN keys:

  - `countryName`
  - `stateOrProvinceName`
  - `localityName`
  - `organizationName`
  - `organizationalUnitName`
  - `commonName`
  - `emailAddress`

- `CONFIG_DEFAULT: dict[str, object]`  
  Default configuration dictionary:

  - `digest_alg`: `"sha512"`
  - `private_key_bits`: `2048`
  - `private_key_type`: `"RSA"`
  - `encrypt_key`: `False`
  - `valid_days`: `365`

## Functions

- `slugify(value: str) -> str`  
  Convert an arbitrary string into a filesystem-safe slug.

- `make_cert_subdir(base_output_dir, dn, label) -> Path`  
  Create a unique subdirectory for a certificate set based on:

  - `commonName` (preferred)
  - `label` (e.g. config filename stem)
  - Fallback to `"cert"` with numeric suffixes.

- `prepare_output_dir(path: Path | None) -> Path | None`  
  Ensure the output directory exists (if one is requested).
