"""
Example configuration generation for the ``lupaxa.certtool`` package.

This module provides helpers for constructing and emitting a sample JSON
configuration that can be used as a starting point for users. The example
configuration includes both a DN block and a config block, demonstrating
typical fields such as:

* ``commonName`` and other DN attributes.
* Digest algorithm and key size.
* Certificate validity period.
* An example ``subject_alt_names`` array for SAN support.

The JSON structure produced by :func:`build_example_config` is compatible
with :func:`lupaxa.certtool.config.load_json_config`.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Internal exceptions
# ---------------------------------------------------------------------------
from .exceptions import OutputError


def build_example_config() -> dict[str, Any]:
    """
    Construct an example configuration dictionary.

    Returns
    -------
    dict
        A dictionary with top-level keys ``"dn"`` and ``"config"``. The
        ``"dn"`` key contains a DN (Distinguished Name) example, while the
        ``"config"`` key contains certificate generation parameters,
        including an example ``"subject_alt_names"`` array illustrating how
        to configure DNS Subject Alternative Names.
    """
    return {
        "dn": {
            "countryName": "UK",
            "stateOrProvinceName": "Somerset",
            "localityName": "Glastonbury",
            "organizationName": "The Lupaxa Project",
            "organizationalUnitName": "Certificate Tooling",
            "commonName": "example.lupaxa.test",
            "emailAddress": "admin@example.test",
        },
        "config": {
            "digest_alg": "sha512",
            "private_key_bits": 2048,
            "private_key_type": "RSA",
            "encrypt_key": False,
            "valid_days": 365,
            # Example SAN entries; these are optional and can be omitted.
            "subject_alt_names": [
                "example.lupaxa.test",
                "www.example.lupaxa.test",
            ],
        },
    }


def generate_example_config(example_file: Path | None = None) -> None:
    """
    Generate and emit an example JSON configuration.

    Parameters
    ----------
    example_file:
        If ``None``, the configuration is written to stdout. If a path is
        provided, the JSON is written to that file instead. Any filesystem
        errors are wrapped in :class:`OutputError`.
    """
    config_dict = build_example_config()
    json_str = json.dumps(config_dict, indent=2)

    if example_file is None:
        # stdout mode
        print(json_str)
        return

    try:
        example_file.write_text(json_str + "\n", encoding="utf-8")
    except OSError as exc:  # pragma: no cover - defensive
        raise OutputError(f"Unable to write example config to {example_file}: {exc}") from exc


# EOF
