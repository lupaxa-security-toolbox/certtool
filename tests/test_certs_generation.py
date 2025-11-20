"""
Tests for certificate generation, serialization, and output helpers.

This module exercises the high-level programmatic API:

* :func:`lupaxa.certtool.generate_from_dn_and_config`
* :func:`lupaxa.certtool.generate_from_json_file`

and the orchestration helper:

* :func:`lupaxa.certtool.certs.handle_single_cert`

The focus is on verifying that PEM bundles are structurally valid, can be
parsed by :mod:`cryptography`, and are written correctly to stdout or disk.
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
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import NameOID

# ---------------------------------------------------------------------------
# Internal certificate generation utilities
# ---------------------------------------------------------------------------
from lupaxa.certtool import CONFIG_DEFAULT, generate_from_dn_and_config, generate_from_json_file  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.certs import handle_single_cert  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.exceptions import ConfigError  # pyright: ignore[reportMissingImports]


def _minimal_dn() -> dict:
    """
    Build a minimal but valid DN dictionary for test purposes.

    The returned dictionary always includes a ``commonName`` entry, which is
    required by the library's DN validation logic.
    """
    return {"commonName": "unit-test.lupaxa.test"}


def _minimal_cfg() -> dict:
    """
    Construct a basic configuration dictionary derived from CONFIG_DEFAULT.

    The returned configuration enforces RSA as the private key type and
    explicitly sets ``encrypt_key`` to False to simplify PEM parsing in tests.
    """
    cfg = dict(CONFIG_DEFAULT)
    cfg["private_key_type"] = "RSA"
    cfg["encrypt_key"] = False
    return cfg


def test_generate_from_dn_and_config_produces_valid_pems() -> None:
    """
    Ensure that :func:`generate_from_dn_and_config` returns a PEM bundle that
    can be parsed by :mod:`cryptography`.

    The test validates:

    * Presence of PEM headers for certificate, CSR, and private key.
    * That the certificate/CSR subjects include the expected commonName.
    * That the private key can be loaded without a passphrase.
    """
    dn = _minimal_dn()
    cfg = _minimal_cfg()

    bundle = generate_from_dn_and_config(dn, cfg)

    # Basic non-empty checks and PEM headers
    assert bundle.certificate_pem.startswith(b"-----BEGIN CERTIFICATE-----")
    assert bundle.csr_pem.startswith(b"-----BEGIN CERTIFICATE REQUEST-----")
    assert bundle.private_key_pem.startswith(b"-----BEGIN PRIVATE KEY-----")

    # Parse certificate
    cert = x509.load_pem_x509_certificate(bundle.certificate_pem)
    assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == dn["commonName"]

    # Parse CSR
    csr = x509.load_pem_x509_csr(bundle.csr_pem)
    assert csr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == dn["commonName"]

    # Parse private key
    key = load_pem_private_key(bundle.private_key_pem, password=None)
    assert isinstance(key, RSAPrivateKey)


def test_generate_from_dn_and_config_rejects_non_rsa() -> None:
    """
    Verify that non-RSA key types are rejected by the programmatic API.

    The library currently only supports RSA private keys, so attempting to
    use a different ``private_key_type`` should result in a ConfigError.
    """
    dn = _minimal_dn()
    cfg = _minimal_cfg()
    cfg["private_key_type"] = "EC"

    with pytest.raises(ConfigError):
        generate_from_dn_and_config(dn, cfg)


def test_generate_from_json_file_roundtrip(tmp_path: Path) -> None:
    """
    Confirm that :func:`generate_from_json_file` correctly processes a JSON
    configuration file and returns a non-empty PEM bundle.

    The configuration file is created dynamically from a minimal DN and
    configuration dictionary.
    """
    cfg_path = tmp_path / "cert.json"
    payload = {
        "dn": _minimal_dn(),
        "config": _minimal_cfg(),
    }
    cfg_path.write_text(json.dumps(payload), encoding="utf-8")

    bundle = generate_from_json_file(cfg_path)
    assert bundle.certificate_pem
    assert bundle.csr_pem
    assert bundle.private_key_pem


def test_handle_single_cert_writes_to_stdout(capsys) -> None:
    """
    Validate that :func:`handle_single_cert` can emit PEM artifacts to stdout
    when no output directory is specified.

    The test checks for the presence of the label separator and PEM headers
    in the captured output.
    """
    dn = _minimal_dn()
    cfg = _minimal_cfg()

    handle_single_cert(dn, cfg, label="stdout-test", output_dir=None)

    captured = capsys.readouterr()
    out = captured.out

    assert "########## CONFIG: stdout-test ##########" in out
    assert "BEGIN CERTIFICATE" in out
    assert "BEGIN CERTIFICATE REQUEST" in out
    assert "BEGIN PRIVATE KEY" in out


def test_handle_single_cert_writes_to_directory(tmp_path: Path) -> None:
    """
    Check that :func:`handle_single_cert` writes PEM artifacts into a
    per-certificate subdirectory when an output directory is provided.

    The test asserts that:

    * Exactly one subdirectory is created under the target directory.
    * The subdirectory contains ``cert.pem``, ``csr.pem``, and ``key.pem``.
    * The certificate file appears to contain PEM data.
    """
    dn = _minimal_dn()
    cfg = _minimal_cfg()

    handle_single_cert(dn, cfg, label="dir-test", output_dir=tmp_path)

    subdirs = [p for p in tmp_path.iterdir() if p.is_dir()]
    assert len(subdirs) == 1
    subdir = subdirs[0]

    cert_path = subdir / "cert.pem"
    csr_path = subdir / "csr.pem"
    key_path = subdir / "key.pem"

    assert cert_path.exists()
    assert csr_path.exists()
    assert key_path.exists()

    cert_bytes = cert_path.read_bytes()
    assert b"BEGIN CERTIFICATE" in cert_bytes


def test_generate_from_dn_and_config_with_encrypted_key() -> None:
    """
    Verify that when ``encrypt_key`` is True and a ``passphrase`` is supplied,
    the private key is serialized in encrypted form and can only be loaded
    with the correct password.
    """
    dn = {"commonName": "encrypted.lupaxa.test"}
    cfg = dict(CONFIG_DEFAULT)
    cfg.update(
        {
            "digest_alg": "sha256",
            "private_key_type": "RSA",
            "encrypt_key": True,
            "passphrase": "EXAMPLE_ONLY_NOT_A_REAL_PASSWORD",
        }
    )

    bundle = generate_from_dn_and_config(dn, cfg)

    # Loading without a password should fail
    with pytest.raises((TypeError, ValueError)):
        load_pem_private_key(bundle.private_key_pem, password=None)

    # Loading with the correct password should succeed
    key = load_pem_private_key(
        bundle.private_key_pem,
        password=b"EXAMPLE_ONLY_NOT_A_REAL_PASSWORD",  # NOSONAR - test-only dummy password
    )
    assert isinstance(key, RSAPrivateKey)


# EOF
