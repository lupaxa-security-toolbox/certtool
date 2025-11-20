"""
Utility functions and shared constants for the certificate generation library.

This module contains:

* Common configuration constants (DN keys, defaults).
* A digest type alias compatible with :mod:`cryptography`.
* A filesystem helper for preparing output directories.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
from pathlib import Path
from typing import (
    Any,
    Union,
)

# ---------------------------------------------------------------------------
# Third-party cryptography primitives
# ---------------------------------------------------------------------------
from cryptography.hazmat.primitives import hashes

# ---------------------------------------------------------------------------
# Internal exceptions
# ---------------------------------------------------------------------------
from .exceptions import OutputError

# ---------------------------------------------------------------------------
# Shared configuration constants
# ---------------------------------------------------------------------------

DN_KEYS = [
    "countryName",
    "stateOrProvinceName",
    "localityName",
    "organizationName",
    "organizationalUnitName",
    "commonName",
    "emailAddress",
]

CONFIG_DEFAULT: dict[str, Any] = {
    "digest_alg": "sha512",
    "private_key_bits": 2048,
    "private_key_type": "RSA",
    "encrypt_key": False,
    "valid_days": 365,
    "subject_alt_names": [],
}

#: Type alias for digest algorithms allowed by :mod:`cryptography` for signing.
DigestAlgorithm = Union[hashes.SHA256, hashes.SHA384, hashes.SHA512]


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def prepare_output_dir(path: Path | None) -> Path | None:
    """
    Ensure that the output directory exists, if requested.

    Parameters
    ----------
    path:
        The requested output directory path, or ``None`` if stdout-only output
        is desired.

    Returns
    -------
    Path | None
        The same path if created/verified successfully, or ``None`` if no
        output directory was requested.

    Raises
    ------
    OutputError
        If the directory cannot be created or accessed.
    """
    if path is None:
        return None
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OutputError(f"Unable to create output directory {path}: {exc}") from exc
    return path


# EOF
