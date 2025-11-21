"""
Cryptographic primitives and high-level generation API.

This module is responsible for:

* Constructing X.509 subject names.
* Generating RSA key pairs.
* Creating CSRs and self-signed certificates.
* Serializing artifacts into PEM bundles.
* Writing PEM data either to stdout or to per-certificate directories.
* Providing a programmatic API for generation from JSON or in-memory config.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
from dataclasses import dataclass
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Third-party cryptography primitives
# ---------------------------------------------------------------------------
from cryptography import x509
from cryptography.hazmat.primitives import (
    hashes,
    serialization,
)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    BestAvailableEncryption,
    KeySerializationEncryption,
    NoEncryption,
)
from cryptography.x509.oid import NameOID

# ---------------------------------------------------------------------------
# Internal configuration helpers
# ---------------------------------------------------------------------------
from .config import (
    load_json_config,
    merge_settings_json,
    validate_dn,
)

# ---------------------------------------------------------------------------
# Internal exceptions
# ---------------------------------------------------------------------------
from .exceptions import (
    CertToolError,
    ConfigError,
    GenerationError,
    OutputError,
)

# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------
from .utils import DigestAlgorithm

# ---------------------------------------------------------------------------
# Digests we permit
# ---------------------------------------------------------------------------

ALLOWED_DIGESTS: dict[str, type[DigestAlgorithm]] = {
    "sha256": hashes.SHA256,
    "sha384": hashes.SHA384,
    "sha512": hashes.SHA512,
}


@dataclass
class CertComponents:
    """Container for in-memory certificate-related cryptography objects.

    Attributes
    ----------
    private_key:
        The generated RSA private key.
    csr:
        The certificate signing request built from the DN and private key.
    cert:
        The self-signed X.509 certificate.

    """

    private_key: rsa.RSAPrivateKey
    csr: x509.CertificateSigningRequest
    cert: x509.Certificate


@dataclass
class PemBundle:
    """
    Container for serialized PEM-encoded artifacts.

    Attributes
    ----------
    certificate_pem:
        The self-signed certificate in PEM format.
    csr_pem:
        The certificate signing request in PEM format.
    private_key_pem:
        The private key in PEM format, encrypted or unencrypted depending on
        configuration.

    """

    certificate_pem: bytes
    csr_pem: bytes
    private_key_pem: bytes


# ---------------------------------------------------------------------------
# X.509 name and digest helpers
# ---------------------------------------------------------------------------


def build_x509_name(dn: dict[str, str]) -> x509.Name:
    """
    Construct a :class:`cryptography.x509.Name` from a DN (Distinguished Name) dict.

    Parameters
    ----------
    dn:
        A dictionary containing zero or more keys such as ``"commonName"`` or
        ``"organizationName"``.

    Returns
    -------
    x509.Name
        A ``Name`` object with attributes populated for keys present in ``dn``.
        Keys that are not present or have falsy values are skipped.

    """
    name_attributes = []

    if dn.get("countryName"):
        name_attributes.append(x509.NameAttribute(NameOID.COUNTRY_NAME, dn["countryName"]))

    if dn.get("stateOrProvinceName"):
        name_attributes.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, dn["stateOrProvinceName"]))

    if dn.get("localityName"):
        name_attributes.append(x509.NameAttribute(NameOID.LOCALITY_NAME, dn["localityName"]))

    if dn.get("organizationName"):
        name_attributes.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, dn["organizationName"]))

    if dn.get("organizationalUnitName"):
        name_attributes.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, dn["organizationalUnitName"]))

    if dn.get("commonName"):
        name_attributes.append(x509.NameAttribute(NameOID.COMMON_NAME, dn["commonName"]))

    if dn.get("emailAddress"):
        name_attributes.append(x509.NameAttribute(NameOID.EMAIL_ADDRESS, dn["emailAddress"]))

    return x509.Name(name_attributes)


def get_digest(digest_name: str) -> DigestAlgorithm:
    """
    Resolve a digest algorithm name to a concrete :class:`hashes.HashAlgorithm` instance.

    Parameters
    ----------
    digest_name:
        A string name such as ``"sha256"``, ``"sha384"``, or ``"sha512"``.
        The comparison is case-insensitive and accepts dashed variants such as
        ``"sha-256"``.

    Returns
    -------
    DigestAlgorithm
        An instance of :class:`SHA256`, :class:`SHA384` or :class:`SHA512`.

    Raises
    ------
    ConfigError
        If the digest algorithm is unknown or explicitly disallowed.
    """
    key = digest_name.lower()
    try:
        return ALLOWED_DIGESTS[key]()  # instance
    except KeyError as exc:
        raise ConfigError(f"Unsupported digest: {key!r}") from exc


# ---------------------------------------------------------------------------
# Key, CSR, and certificate generation
# ---------------------------------------------------------------------------


def generate_key_pair(bits: int) -> rsa.RSAPrivateKey:
    """
    Generate an RSA private key of the requested size.

    Parameters
    ----------
    bits:
        Key size in bits (for example, 2048, 3072, 4096).

    Returns
    -------
    rsa.RSAPrivateKey
        The generated private key.

    Raises
    ------
    GenerationError
        If RSA key generation fails for any reason.
    """
    try:
        return rsa.generate_private_key(public_exponent=65537, key_size=bits)
    except Exception as exc:  # pragma: no cover - defensive
        raise GenerationError(f"Failed to generate RSA key ({bits} bits): {exc}") from exc


def generate_csr(private_key: rsa.RSAPrivateKey, subject: x509.Name, digest_alg: str) -> x509.CertificateSigningRequest:
    """
    Generate a certificate signing request (CSR) for the given subject.

    Parameters
    ----------
    private_key:
        The RSA private key used to sign the CSR.
    subject:
        The X.509 subject name for the CSR.
    digest_alg:
        Digest algorithm name to use for signing (for example, ``"sha256"``).

    Returns
    -------
    x509.CertificateSigningRequest
        A signed CSR object.

    Raises
    ------
    ConfigError
        If the digest algorithm is invalid or unsupported.
    GenerationError
        If CSR creation or signing fails.
    """
    try:
        builder = x509.CertificateSigningRequestBuilder().subject_name(subject)
        return builder.sign(private_key=private_key, algorithm=get_digest(digest_alg))
    except CertToolError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise GenerationError(f"Failed to generate CSR: {exc}") from exc


def generate_self_signed_cert(private_key: rsa.RSAPrivateKey, subject: x509.Name, digest_alg: str, valid_days: int, subject_alt_names: list[str] | None = None) -> x509.Certificate:
    """
    Generate a self-signed X.509 certificate.

    Parameters
    ----------
    private_key:
        The RSA private key whose public component will be embedded in the
        certificate and used for signing.
    subject:
        The X.509 subject name, which also acts as the issuer name for
        self-signed certificates.
    digest_alg:
        Digest algorithm name to use for signing (for example, ``"sha256"``).
    valid_days:
        Number of days for which the certificate should be valid.

    Returns
    -------
    x509.Certificate
        A signed X.509 certificate object.

    Raises
    ------
    ConfigError
        If the digest algorithm is invalid or unsupported.
    GenerationError
        If certificate construction or signing fails.
    """
    try:
        now = datetime.now(timezone.utc)

        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1))
            .not_valid_after(now + timedelta(days=valid_days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        )

        if subject_alt_names:
            san = x509.SubjectAlternativeName([x509.DNSName(name) for name in subject_alt_names])
            builder = builder.add_extension(san, critical=False)

        return builder.sign(private_key=private_key, algorithm=get_digest(digest_alg))
    except CertToolError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise GenerationError(f"Failed to generate self-signed certificate: {exc}") from exc


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def create_cert_components(dn: dict[str, Any], cfg: dict[str, Any]) -> CertComponents:
    """
    Generate key, CSR, and certificate objects from DN and CONFIG.

    Parameters
    ----------
    dn:
        Distinguished Name dictionary, validated by :func:`validate_dn`.
    cfg:
        Configuration dictionary, including keys such as:

        * ``"digest_alg"``: digest algorithm name.
        * ``"private_key_bits"``: key size.
        * ``"valid_days"``: certificate validity in days.

    Returns
    -------
    CertComponents
        An object bundling the private key, CSR, and certificate.

    Raises
    ------
    GenerationError
        If key, CSR, or certificate generation fails.
    ConfigError
        If digest or other configuration values are invalid.
    """
    subject = build_x509_name(dn)
    private_key = generate_key_pair(cfg["private_key_bits"])
    csr = generate_csr(private_key=private_key, subject=subject, digest_alg=cfg["digest_alg"])
    cert = generate_self_signed_cert(private_key=private_key, subject=subject, digest_alg=cfg["digest_alg"], valid_days=cfg["valid_days"], subject_alt_names=cfg.get("subject_alt_names") or None)
    return CertComponents(private_key=private_key, csr=csr, cert=cert)


def serialize_cert_components(components: CertComponents, encrypt_key: bool, passphrase: str | None) -> PemBundle:
    """
    Serialize certificate components into PEM-encoded bytes.

    Parameters
    ----------
    components:
        The in-memory certificate components (private key, CSR, certificate).
    encrypt_key:
        Whether to encrypt the private key using a hard-coded passphrase
        placeholder or to leave it unencrypted.

    Returns
    -------
    PemBundle
        A bundle containing PEM-encoded certificate, CSR, and private key.

    Raises
    ------
    GenerationError
        If serialization of any component fails.
    """
    encryption: KeySerializationEncryption

    if encrypt_key:
        if not passphrase:
            raise ConfigError("encrypt_key is true but no passphrase was provided. Set 'passphrase' in the JSON config or via --passphrase.")
        encryption = BestAvailableEncryption(passphrase.encode("utf-8"))
    else:
        encryption = NoEncryption()

    try:
        private_key_pem = components.private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=encryption)
        csr_pem = components.csr.public_bytes(serialization.Encoding.PEM)
        cert_pem = components.cert.public_bytes(serialization.Encoding.PEM)
    except Exception as exc:  # pragma: no cover - defensive
        raise GenerationError(f"Failed to serialize certificate artifacts: {exc}") from exc

    return PemBundle(certificate_pem=cert_pem, csr_pem=csr_pem, private_key_pem=private_key_pem)


# ---------------------------------------------------------------------------
# Filesystem naming and output helpers
# ---------------------------------------------------------------------------


def slugify(value: str) -> str:
    """
    Produce a filesystem-friendly slug from the given string.

    Parameters
    ----------
    value:
        The input string (for example, a commonName or filename stem).

    Returns
    -------
    str
        A lowercase, stripped string containing only alphanumerics, dots,
        dashes, and underscores, with spaces converted to underscores. If
        the result is empty, ``"cert"`` is returned.
    """
    value = value.strip().lower()
    if not value:
        return "cert"
    chars = []
    for ch in value:
        if ch.isalnum() or ch in {".", "-", "_"}:
            chars.append(ch)
        elif ch.isspace():
            chars.append("_")
        else:
            # drop other punctuation
            continue
    slug = "".join(chars).strip("._-")
    return slug or "cert"


def make_cert_subdir(base_output_dir: Path, dn: dict[str, Any], label: str | None) -> Path:
    """
    Create a unique subdirectory for a single certificate set.

    Naming preference
    -----------------
    1) Use ``dn["commonName"]`` if present.
    2) Otherwise, use ``label`` (typically the config filename without extension).
    3) Fallback to ``"cert"``.

    If a directory with the chosen name already exists, a numeric suffix
    (``-1``, ``-2``, ...) is appended to avoid overwriting.

    Parameters
    ----------
    base_output_dir:
        Root directory under which subdirectories will be created.
    dn:
        Distinguished Name dictionary for the certificate.
    label:
        Optional label (for example, originating config filename).

    Returns
    -------
    Path
        The path to the created subdirectory.

    Raises
    ------
    OutputError
        If the subdirectory cannot be created due to filesystem issues.
    """
    cn = str(dn.get("commonName") or "").strip()
    if cn:
        base_name = slugify(cn)
    elif label:
        base_name = slugify(Path(label).stem)
    else:
        base_name = "cert"

    candidate = base_output_dir / base_name
    if not candidate.exists():
        try:
            candidate.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            raise OutputError(f"Unable to create directory {candidate}: {exc}") from exc
        return candidate

    # Avoid overwriting: add numeric suffix
    counter = 1
    while True:
        candidate = base_output_dir / f"{base_name}-{counter}"
        if not candidate.exists():
            try:
                candidate.mkdir(parents=True, exist_ok=False)
            except OSError as exc:
                raise OutputError(f"Unable to create directory {candidate}: {exc}") from exc
            return candidate
        counter += 1


def write_bundle_to_stdout(bundle: PemBundle, label: str | None) -> None:
    """
    Write PEM artifacts to stdout in a human-readable format.

    Parameters
    ----------
    bundle:
        A :class:`PemBundle` containing certificate, CSR, and private key PEM data.
    label:
        Optional label (for example, config filename) used to delineate
        sections when multiple certificates are printed.
    """
    if label:
        print(f"\n########## CONFIG: {label} ##########\n")

    print("# Self-signed certificate (PEM)")
    print(bundle.certificate_pem.decode("ascii"))

    print("# Certificate Signing Request (CSR, PEM)")
    print(bundle.csr_pem.decode("ascii"))

    print("# Private Key (PEM)")
    print(bundle.private_key_pem.decode("ascii"))


def write_bundle_to_dir(bundle: PemBundle, dn: dict[str, Any], label: str | None, output_dir: Path) -> None:
    """
    Write PEM artifacts to disk in a per-certificate subdirectory.

    Parameters
    ----------
    bundle:
        PEM-encoded certificate, CSR, and private key.
    dn:
        Distinguished Name dictionary for the certificate, used for naming.
    label:
        Optional label (for example, originating config filename), used for
        naming if ``"commonName"`` is not available.
    output_dir:
        Base directory under which the per-certificate subdirectory will
        be created.

    Raises
    ------
    OutputError
        If any file write fails or the subdirectory cannot be created.
    """
    subdir = make_cert_subdir(output_dir, dn, label)
    cert_path = subdir / "cert.pem"
    csr_path = subdir / "csr.pem"
    key_path = subdir / "key.pem"

    try:
        cert_path.write_bytes(bundle.certificate_pem)
        csr_path.write_bytes(bundle.csr_pem)
        key_path.write_bytes(bundle.private_key_pem)
    except OSError as exc:
        raise OutputError(f"Failed to write PEM files in {subdir}: {exc}") from exc


# ---------------------------------------------------------------------------
# High-level orchestration helpers
# ---------------------------------------------------------------------------


def handle_single_cert(dn: dict[str, Any], cfg: dict[str, Any], label: str | None, output_dir: Path | None) -> None:
    """
    Run the full pipeline for a single certificate and emit output.

    Pipeline steps
    --------------
    1) Generate cryptography objects (key, CSR, certificate).
    2) Serialize them to PEM.
    3) Write them either to stdout or to a per-certificate directory.

    Parameters
    ----------
    dn:
        Distinguished Name dictionary for the certificate.
    cfg:
        Configuration dictionary for key and certificate settings.
    label:
        Optional label to tag the output when writing to stdout or when
        generating directory names.
    output_dir:
        Directory for file output, or ``None`` for stdout-only output.

    Raises
    ------
    CertToolError
        If generation, serialization, or output fails.
    """
    components = create_cert_components(dn, cfg)
    bundle = serialize_cert_components(components, bool(cfg.get("encrypt_key")), cfg.get("passphrase"))
    if output_dir is None:
        write_bundle_to_stdout(bundle, label=label)
    else:
        write_bundle_to_dir(bundle, dn=dn, label=label, output_dir=output_dir)


def generate_from_json_file(path: Path) -> PemBundle:
    """
    Generate a PEM bundle from a JSON configuration file (programmatic API).

    This is a convenience wrapper that combines configuration parsing,
    DN/CONFIG merging, and certificate generation into a single call.

    Parameters
    ----------
    path:
        Path to the JSON configuration file.

    Returns
    -------
    PemBundle
        PEM-encoded certificate, CSR, and private key.

    Raises
    ------
    CertToolError
        If configuration is invalid or generation fails.
    """
    json_dn, json_cfg = load_json_config(path)
    dn, cfg = merge_settings_json(json_dn, json_cfg)
    components = create_cert_components(dn, cfg)
    return serialize_cert_components(components, bool(cfg.get("encrypt_key")), cfg.get("passphrase"))


def generate_from_dn_and_config(dn: dict[str, Any], cfg: dict[str, Any]) -> PemBundle:
    """
    Generate a PEM bundle from explicit DN and CONFIG dictionaries.

    This is useful for purely programmatic usage where configuration is
    not sourced from JSON or CLI.

    Parameters
    ----------
    dn:
        Distinguished Name dictionary. Must at least contain a non-empty
        ``"commonName"`` field.
    cfg:
        Configuration dictionary. Expected keys include:

        * ``"digest_alg"`` (for example, ``"sha256"``, ``"sha512"``)
        * ``"private_key_bits"`` (for example, 2048)
        * ``"private_key_type"`` (must be ``"RSA"``)
        * ``"encrypt_key"`` (bool)
        * ``"valid_days"`` (int)

        Missing keys are *not* automatically filled here; callers should
        merge with defaults themselves if required.

    Returns
    -------
    PemBundle
        PEM-encoded certificate, CSR, and private key.

    Raises
    ------
    ConfigError
        If the DN or configuration values are invalid.
    GenerationError
        If any generation step fails.
    """
    validate_dn(dn)

    if cfg.get("private_key_type", "").upper() != "RSA":
        raise ConfigError(f"Unsupported private_key_type {cfg.get('private_key_type')!r}; only 'RSA' is supported.")

    # Coerce a few known fields, but assume caller mostly passed correct types
    if "private_key_bits" in cfg:
        cfg["private_key_bits"] = int(cfg["private_key_bits"])
    if "valid_days" in cfg:
        cfg["valid_days"] = int(cfg["valid_days"])

    components = create_cert_components(dn, cfg)
    return serialize_cert_components(components, bool(cfg.get("encrypt_key")), cfg.get("passphrase"))


# EOF
