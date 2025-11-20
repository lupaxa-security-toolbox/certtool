"""
Configuration loading and validation for the certificate generation library.

This module handles:

* Reading JSON configuration files.
* Splitting values into DN and CONFIG dictionaries.
* Type coercion for key parameters.
* Validation of DN requirements and private key type.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Internal exceptions (alphabetically first among local imports)
# ---------------------------------------------------------------------------
from .exceptions import ConfigError

# ---------------------------------------------------------------------------
# Internal shared constants (alphabetically next: .utils)
# ---------------------------------------------------------------------------
from .utils import (
    CONFIG_DEFAULT,
    DN_KEYS,
)


def _coerce_bool(value: object) -> bool:
    """
    Convert an arbitrary JSON value to a boolean, if possible.

    Parameters
    ----------
    value:
        A value from a JSON configuration, such as a bool, number, or string.

    Returns
    -------
    bool
        The coerced boolean value.

    Raises
    ------
    ConfigError
        If the value cannot be reasonably interpreted as a boolean.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "true", "yes", "y", "on"}:
            return True
        if v in {"0", "false", "no", "n", "off"}:
            return False
    raise ConfigError(f"Cannot coerce {value!r} to bool")


def _read_json_file(path: Path) -> object:
    """
    Read and parse JSON data from a file.

    Parameters
    ----------
    path:
        Path to the JSON configuration file.

    Returns
    -------
    Any
        The parsed JSON object (usually a dict).

    Raises
    ------
    ConfigError
        If the file cannot be read or the contents are not valid JSON.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Unable to read JSON config {path}: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config {path}: {exc}") from exc


def _ensure_dict_top_level(data: object, path: Path) -> dict[str, Any]:
    """
    Ensure that the parsed JSON data has a dict as the top-level object.

    Parameters
    ----------
    data:
        The parsed JSON data (result of :func:`json.loads`).
    path:
        Path to the JSON file, used for error reporting.

    Returns
    -------
    dict[str, Any]
        The JSON data cast to a dict.

    Raises
    ------
    ConfigError
        If the top-level JSON object is not a dict.
    """
    if not isinstance(data, dict):
        raise ConfigError(f"JSON config {path} must be an object at the top level")
    return data


def _extract_explicit_blocks(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Extract DN and CONFIG dictionaries from explicit 'dn' and 'config' blocks.

    Parameters
    ----------
    data:
        A JSON object containing optional ``"dn"`` and ``"config"`` keys.

    Returns
    -------
    (dn, cfg) : tuple[dict[str, Any], dict[str, Any]]
        Two dictionaries: one for DN values, one for CONFIG values.
        Keys not present or not mapping types are ignored silently.
    """
    dn: dict[str, Any] = {}
    cfg: dict[str, Any] = {}

    if isinstance(data.get("dn"), dict):
        dn.update(data["dn"])
    if isinstance(data.get("config"), dict):
        cfg.update(data["config"])

    return dn, cfg


def _extract_flat_config(data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Extract DN and CONFIG values from a flat JSON object.

    Parameters
    ----------
    data:
        A JSON object where DN and CONFIG keys are at the top level.

    Returns
    -------
    (dn, cfg) : tuple[dict[str, Any], dict[str, Any]]
        A DN dict containing keys from :data:`DN_KEYS`, and a CONFIG dict
        containing keys from :data:`CONFIG_DEFAULT`. Unknown keys are ignored.
    """
    dn: dict[str, Any] = {}
    cfg: dict[str, Any] = {}

    for key, value in data.items():
        if key in DN_KEYS:
            dn[key] = value
        elif key in CONFIG_DEFAULT or key == "passphrase":
            cfg[key] = value
        # Unknown keys are silently ignored

    return dn, cfg


def _coerce_config_types(cfg: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize types of known CONFIG values (for example, ints, bools).

    Parameters
    ----------
    cfg:
        Configuration dictionary potentially containing values with
        non-native types (for example, strings for integers or booleans).

    Returns
    -------
    dict[str, Any]
        The same dictionary, with ``"private_key_bits"``, ``"valid_days"`` and
        ``"encrypt_key"`` coerced to int/bool where present.

    Raises
    ------
    ConfigError
        If boolean coercion fails via :func:`_coerce_bool`.
    """
    if "private_key_bits" in cfg:
        cfg["private_key_bits"] = int(cfg["private_key_bits"])
    if "valid_days" in cfg:
        cfg["valid_days"] = int(cfg["valid_days"])
    if "encrypt_key" in cfg:
        cfg["encrypt_key"] = _coerce_bool(cfg["encrypt_key"])
    return cfg


def load_json_config(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Load DN and CONFIG data from a JSON configuration file.

    Supported JSON shapes
    ---------------------

    1) Explicit blocks::

        {
          "dn": { ... },
          "config": { ... }
        }

    2) Flat dictionary::

        {
          "countryName": "...",
          "digest_alg": "...",
          ...
        }

    In the flat case, keys are split between :data:`DN_KEYS` and
    :data:`CONFIG_DEFAULT`.

    Parameters
    ----------
    path:
        Path to the JSON configuration file.

    Returns
    -------
    (dn, cfg) : tuple[dict[str, Any], dict[str, Any]]
        DN and CONFIG dictionaries extracted from the JSON file, with basic
        type coercions applied.

    Raises
    ------
    ConfigError
        If the file cannot be read, contains invalid JSON, is not a dict at
        the top level, or contains invalid values for known fields.
    """
    data_raw = _read_json_file(path)
    data = _ensure_dict_top_level(data_raw, path)

    if "dn" in data or "config" in data:
        dn, cfg = _extract_explicit_blocks(data)
    else:
        dn, cfg = _extract_flat_config(data)

    cfg = _coerce_config_types(cfg)
    return dn, cfg


def validate_dn(dn: dict[str, Any]) -> None:
    """
    Validate the DN dictionary to ensure required fields are present.

    Parameters
    ----------
    dn:
        The DN dictionary to validate.

    Raises
    ------
    ConfigError
        If ``dn`` is empty or the ``"commonName"`` field is missing or blank.
    """
    if not dn:
        raise ConfigError("DN is empty. You must supply DN attributes (at least 'commonName') either via CLI or JSON configuration.")

    cn = dn.get("commonName")
    if not cn or not str(cn).strip():
        raise ConfigError("DN is missing 'commonName'. Provide it in the JSON config or via CLI.")


def merge_settings_json(
    json_dn: dict[str, Any] | None,
    json_cfg: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Merge JSON DN/CONFIG with defaults for config-driven modes.

    Parameters
    ----------
    json_dn:
        DN dictionary extracted from JSON (or None).
    json_cfg:
        CONFIG dictionary extracted from JSON (or None).

    Returns
    -------
    (dn, cfg) : tuple[dict[str, Any], dict[str, Any]]
        DN and CONFIG dictionaries, where:

        * DN is taken solely from ``json_dn`` (no defaults).
        * CONFIG starts from :data:`CONFIG_DEFAULT` and then applies
          ``json_cfg``.

    Raises
    ------
    ConfigError
        If the private key type is unsupported or the DN is invalid.
    """
    dn: dict[str, Any] = {}
    if json_dn:
        dn.update(json_dn)

    cfg = dict(CONFIG_DEFAULT)
    if json_cfg:
        cfg.update(json_cfg)

    # Ensure types for CONFIG
    cfg["private_key_bits"] = int(cfg["private_key_bits"])
    cfg["valid_days"] = int(cfg["valid_days"])

    if cfg.get("private_key_type", "").upper() != "RSA":
        raise ConfigError(f"Unsupported private_key_type {cfg['private_key_type']!r}; only 'RSA' is supported.")

    # DN must be valid
    validate_dn(dn)

    return dn, cfg


# EOF
