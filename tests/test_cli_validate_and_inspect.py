"""
Tests for CLI configuration validation and certificate inspection modes.

This module exercises the following CLI features exposed via
:func:`lupaxa.certtool.cli.run`:

* ``--validate-config``: validates a JSON configuration file without generating
  any certificates.
* ``--inspect-cert``: inspects an existing PEM-encoded certificate and prints
  basic metadata such as subject, issuer, validity period, and SAN entries.
"""

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import argparse
import json

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pytest

# ---------------------------------------------------------------------------
# Internal CLI and generation helpers
# ---------------------------------------------------------------------------
from lupaxa.certtool import CONFIG_DEFAULT, generate_from_dn_and_config  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.cli import run  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.exceptions import ConfigError  # pyright: ignore[reportMissingImports]


def _base_args() -> argparse.Namespace:
    """
    Construct a minimal argument namespace with all fields expected by
    :func:`run`, defaulting to a non-generating, non-version mode.

    This helper mirrors the shape of :class:`argparse.Namespace` produced
    by :func:`lupaxa.certtool.cli.parse_args`, but is tailored for unit
    testing via direct calls to :func:`run`.
    """
    return argparse.Namespace(
        # Meta / mode flags
        version=False,
        generate_example=False,
        example_file=None,
        validate_config=None,
        inspect_cert=None,
        # Generation modes
        config=None,
        config_dir=None,
        output_dir=None,
        # DN CLI options (all unset)
        countryName=None,
        stateOrProvinceName=None,
        localityName=None,
        organizationName=None,
        organizationalUnitName=None,
        commonName=None,
        emailAddress=None,
        # CONFIG CLI options (all unset)
        digest_alg=None,
        private_key_bits=None,
        private_key_type=None,
        valid_days=None,
        encrypt_key=None,
    )


def test_validate_config_success(tmp_path, capsys) -> None:
    """
    Verify that ``--validate-config`` succeeds for a well-formed JSON
    configuration and prints a confirmation message.

    The test writes a minimal configuration file to a temporary directory,
    invokes :func:`run` in validate-config mode, and asserts that no
    exceptions are raised and that stdout contains a confirmation string.
    """
    cfg_path = tmp_path / "valid.json"

    config_data = {
        "dn": {
            "commonName": "valid.lupaxa.test",
        },
        "config": {
            "digest_alg": "sha256",
            "private_key_bits": 2048,
            "private_key_type": "RSA",
            "encrypt_key": False,
            "valid_days": 365,
        },
    }

    cfg_path.write_text(json.dumps(config_data), encoding="utf-8")

    args = _base_args()
    args.validate_config = cfg_path

    run(args)

    captured = capsys.readouterr()
    out = captured.out.strip()
    assert "valid" in out.lower()
    assert str(cfg_path) in out


def test_validate_config_failure_raises_config_error(tmp_path) -> None:
    """
    Verify that ``--validate-config`` raises :class:`ConfigError` for an
    invalid configuration, for example when ``commonName`` is missing from
    the DN block.

    The test writes an invalid configuration file and asserts that calling
    :func:`run` in validate-config mode raises the expected exception.
    """
    cfg_path = tmp_path / "invalid.json"

    invalid_config = {
        "dn": {
            # Missing "commonName"
            "countryName": "UK",
        },
        "config": {
            "digest_alg": "sha256",
            "private_key_bits": 2048,
            "private_key_type": "RSA",
            "encrypt_key": False,
            "valid_days": 365,
        },
    }

    cfg_path.write_text(json.dumps(invalid_config), encoding="utf-8")

    args = _base_args()
    args.validate_config = cfg_path

    with pytest.raises(ConfigError):
        run(args)


def test_inspect_cert_prints_basic_metadata(tmp_path, capsys) -> None:
    """
    Verify that ``--inspect-cert`` prints basic certificate metadata,
    including subject information and, when present, SAN entries.

    The test generates a certificate via the programmatic API, writes the
    PEM-encoded certificate to a temporary file, and invokes :func:`run`
    in inspect-cert mode.
    """
    dn = {"commonName": "inspect.lupaxa.test"}
    cfg = dict(CONFIG_DEFAULT)
    cfg.update(
        {
            "digest_alg": "sha256",
            "private_key_type": "RSA",
            "encrypt_key": False,
            "subject_alt_names": ["inspect.lupaxa.test", "alt.lupaxa.test"],
        }
    )

    bundle = generate_from_dn_and_config(dn, cfg)
    cert_path = tmp_path / "cert.pem"
    cert_path.write_bytes(bundle.certificate_pem)

    args = _base_args()
    args.inspect_cert = cert_path

    run(args)

    captured = capsys.readouterr()
    out = captured.out

    # Basic sanity checks on the printed output
    assert "Certificate:" in out
    assert str(cert_path) in out
    assert "Subject:" in out
    assert "Valid from:" in out
    assert "Valid until:" in out
    assert "DNS SANs:" in out
    assert "inspect.lupaxa.test" in out
    assert "alt.lupaxa.test" in out


def test_config_mode_uses_cli_passphrase_for_encryption(tmp_path) -> None:
    """
    Verify that in config-file mode, when ``encrypt_key`` is True but the
    JSON config does not define ``passphrase``, a CLI-supplied passphrase
    is accepted and used for private key encryption.
    """
    cfg_path = tmp_path / "enc.json"

    config_data = {
        "dn": {
            "commonName": "cli-passphrase.lupaxa.test",
        },
        "config": {
            "digest_alg": "sha256",
            "private_key_bits": 2048,
            "private_key_type": "RSA",
            "encrypt_key": True,
            "valid_days": 365,
            # Intentionally no "passphrase" here
        },
    }

    cfg_path.write_text(json.dumps(config_data), encoding="utf-8")

    args = _base_args()
    args.config = cfg_path
    args.passphrase = "cli-secret"
    # Use an output directory to avoid printing large PEM blobs to stdout
    args.output_dir = tmp_path / "out"

    # Should not raise; the passphrase is taken from CLI
    run(args)

    # Sanity check: ensure something was written
    assert any(args.output_dir.iterdir())

# EOF
