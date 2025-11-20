"""
Tests for Subject Alternative Name (SAN) support in generated certificates.

These tests validate that when the configuration includes a
``subject_alt_names`` list, the resulting self-signed certificate contains
a :class:`cryptography.x509.SubjectAlternativeName` extension with the
expected DNS names, and that the extension is absent when the list is not
provided.
"""

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pytest
from cryptography import x509

# ---------------------------------------------------------------------------
# Internal certificate generation API
# ---------------------------------------------------------------------------
from lupaxa.certtool import (  # pyright: ignore[reportMissingImports]
    CONFIG_DEFAULT,
    generate_from_dn_and_config,
)


def test_certificate_contains_configured_san_dns_names() -> None:
    """
    Ensure that when ``subject_alt_names`` is provided in the configuration,
    the generated certificate contains a matching SAN extension with the
    expected DNS names.
    """
    dn = {"commonName": "san.lupaxa.test"}
    cfg = dict(CONFIG_DEFAULT)
    cfg.update(
        {
            "digest_alg": "sha256",
            "private_key_type": "RSA",
            "encrypt_key": False,
            "subject_alt_names": ["example.com", "www.example.com"],
        }
    )

    bundle = generate_from_dn_and_config(dn, cfg)
    cert = x509.load_pem_x509_certificate(bundle.certificate_pem)

    san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    dns_names = san.value.get_values_for_type(x509.DNSName)

    assert dns_names == ["example.com", "www.example.com"]


def test_certificate_without_san_has_no_san_extension() -> None:
    """
    Ensure that if ``subject_alt_names`` is not provided in the configuration,
    the generated certificate does not contain a SAN extension.

    The test asserts that attempting to retrieve the SAN extension raises
    :class:`cryptography.x509.ExtensionNotFound`.
    """
    dn = {"commonName": "nosan.lupaxa.test"}
    cfg = dict(CONFIG_DEFAULT)
    cfg.update(
        {
            "digest_alg": "sha256",
            "private_key_type": "RSA",
            "encrypt_key": False,
        }
    )

    bundle = generate_from_dn_and_config(dn, cfg)
    cert = x509.load_pem_x509_certificate(bundle.certificate_pem)

    with pytest.raises(x509.ExtensionNotFound):
        cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)

# EOF
