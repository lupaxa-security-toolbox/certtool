"""
Tests for JSON configuration loading and DN validation.

This module focuses on:

* Correct parsing of both "explicit blocks" and "flat" JSON configuration
  shapes via :func:`lupaxa.certtool.config.load_json_config`.
* Type coercion and default handling for configuration values.
* Behaviour of :func:`lupaxa.certtool.config.validate_dn` when required
  fields such as ``commonName`` are missing.
"""

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pytest

# ---------------------------------------------------------------------------
# Internal certificate configuration & validation
# ---------------------------------------------------------------------------
from lupaxa.certtool.config import load_json_config, validate_dn  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.exceptions import ConfigError  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.utils import CONFIG_DEFAULT, DN_KEYS  # pyright: ignore[reportMissingImports]


def test_load_json_config_explicit_blocks(tmp_path: Path) -> None:
    """
    Verify that ``{"dn": {...}, "config": {...}}`` shaped JSON is correctly
    split into DN and configuration dictionaries.

    Also checks that basic values are preserved and that type coercion does not
    alter explicitly numeric fields.
    """
    cfg_path = tmp_path / "explicit.json"
    payload = {
        "dn": {
            "commonName": "explicit.lupaxa.test",
            "countryName": "UK",
        },
        "config": {
            "digest_alg": "sha256",
            "private_key_bits": 4096,
            "valid_days": 730,
            "encrypt_key": True,
        },
    }
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")

    dn, cfg = load_json_config(cfg_path)

    assert dn["commonName"] == "explicit.lupaxa.test"
    assert dn["countryName"] == "UK"

    assert cfg["digest_alg"] == "sha256"
    assert cfg["private_key_bits"] == 4096
    assert cfg["valid_days"] == 730
    assert cfg["encrypt_key"] is True


def test_load_json_config_flat_dict(tmp_path: Path) -> None:
    """
    Verify that a flat JSON object containing both DN and configuration keys
    is correctly partitioned and that type coercion is applied where expected.

    Unknown keys in the JSON object should be silently ignored.
    """
    cfg_path = tmp_path / "flat.json"
    payload = {
        "commonName": "flat.lupaxa.test",
        "countryName": "UK",
        "digest_alg": "sha512",
        "private_key_bits": "3072",
        "valid_days": "365",
        "encrypt_key": "false",
        "unknown_key": "ignored",
    }
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")

    dn, cfg = load_json_config(cfg_path)

    assert dn["commonName"] == "flat.lupaxa.test"
    assert dn["countryName"] == "UK"

    # Config is coerced types
    assert cfg["digest_alg"] == "sha512"
    assert cfg["private_key_bits"] == 3072
    assert cfg["valid_days"] == 365
    assert cfg["encrypt_key"] is False
    # Unknown key not present
    assert "unknown_key" not in cfg


def test_validate_dn_requires_common_name() -> None:
    """
    Confirm that :func:`validate_dn` enforces the presence of a non-empty
    ``commonName`` in the DN dictionary.

    The function should raise :class:`ConfigError` when ``commonName`` is
    missing or empty, and succeed silently when it is present.
    """
    dn_missing_cn = {"countryName": "UK"}

    # Expect failure
    with pytest.raises(ConfigError) as exc_info:
        validate_dn(dn_missing_cn)

    # Optional: assert the message contains "commonName"
    assert "commonName" in str(exc_info.value)

    # Expect success
    dn_ok = {"commonName": "ok.lupaxa.test"}
    validate_dn(dn_ok)  # Should not raise


def test_dn_keys_and_config_default_sanity() -> None:
    """
    Perform basic sanity checks on the shared configuration constants.

    This test ensures that:

    * ``DN_KEYS`` contains at least ``"commonName"``.
    * ``CONFIG_DEFAULT`` is a dictionary with expected core keys present.
    """
    assert "commonName" in DN_KEYS
    assert isinstance(CONFIG_DEFAULT, dict)

    for key in ["digest_alg", "private_key_bits", "private_key_type", "valid_days"]:
        assert key in CONFIG_DEFAULT

# EOF
