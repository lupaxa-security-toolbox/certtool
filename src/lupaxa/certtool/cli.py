"""
Command-line interface for the ``lupaxa.certtool`` package.

This module parses CLI arguments, validates the selected operating mode, and
dispatches to the appropriate generation or example-configuration routines.

Supported modes
---------------
* CLI-only certificate generation (DN/config via flags).
* Config file / config directory certificate generation.
* Example JSON configuration generation (``--generate-example``).
* Version reporting (``--version``).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import argparse
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Third-party cryptography primitives
# ---------------------------------------------------------------------------
from cryptography import x509

# ---------------------------------------------------------------------------
# Internal certificate generation (.certs)
# ---------------------------------------------------------------------------
from .certs import handle_single_cert

# ---------------------------------------------------------------------------
# Internal configuration loading & validation (.config)
# ---------------------------------------------------------------------------
from .config import (
    load_json_config,
    merge_settings_json,
    validate_dn,
)

# ---------------------------------------------------------------------------
# Internal example configuration helpers (.example)
# ---------------------------------------------------------------------------
from .example import generate_example_config

# ---------------------------------------------------------------------------
# Internal exceptions (.exceptions)
# ---------------------------------------------------------------------------
from .exceptions import (
    CertToolError,
    ConfigError,
)

# ---------------------------------------------------------------------------
# Internal utilities and shared constants (.utils)
# ---------------------------------------------------------------------------
from .utils import (
    CONFIG_DEFAULT,
    DN_KEYS,
    prepare_output_dir,
)

# ---------------------------------------------------------------------------
# Version information (.version)
# ---------------------------------------------------------------------------
from .version import get_version

# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the ``certtool`` CLI.

    Returns
    -------
    argparse.Namespace
        The parsed arguments, including mode selection flags and DN/config
        options.
    """
    parser = argparse.ArgumentParser(description="Generate self-signed certificate(s), CSR(s), and private key(s).")

    # High-level mode / meta options
    parser.add_argument("-V", "--version", action="store_true", help="Show program version and exit.")
    parser.add_argument("--generate-example", action="store_true", help="Generate an example JSON configuration and exit.")
    parser.add_argument("--example-file", type=Path, help=("When used with --generate-example, write the example JSON configuration to this file instead of stdout."))

    parser.add_argument("--config", type=Path, help="Path to JSON config file for DN and certificate settings.")
    parser.add_argument("--config-dir", type=Path, help="Directory containing JSON config files for bulk generation.")
    parser.add_argument("--output-dir", type=Path, help=("Directory to write outputs into. For each cert, a subdirectory will be created containing cert.pem, csr.pem, key.pem."))
    parser.add_argument("--validate-config", type=Path, metavar="FILE", help="Validate a JSON configuration file and exit without generating certificates.")
    parser.add_argument("--inspect-cert", type=Path, metavar="CERT", help="Inspect an existing PEM-encoded certificate and print basic details.")
    # DN options (no defaults – they must be set via JSON/CLI)
    parser.add_argument("--country-name", dest="countryName", help="Country Name (C). Example: UK")
    parser.add_argument("--state-or-province-name", dest="stateOrProvinceName", help="State or Province Name (ST). Example: Somerset")
    parser.add_argument("--locality-name", dest="localityName", help="Locality Name (L). Example: Glastonbury")
    parser.add_argument("--organization-name", dest="organizationName", help="Organization Name (O).")
    parser.add_argument("--organizational-unit-name", dest="organizationalUnitName", help="Organizational Unit Name (OU).")
    parser.add_argument("--common-name", dest="commonName", help="Common Name (CN). For SSL: hostname; for S/MIME: person's name.")
    parser.add_argument("--email-address", dest="emailAddress", help="Email Address.")

    # CONFIG options
    parser.add_argument("--digest-alg", dest="digest_alg", choices=["sha512", "sha384", "sha256"], help="Digest algorithm to use for signing. Default: sha512")
    parser.add_argument("--private-key-bits", dest="private_key_bits", type=int, help="Private key size in bits. Default: 2048")
    parser.add_argument("--private-key-type", dest="private_key_type", default=None, help="Private key type (currently only RSA is supported).")
    parser.add_argument("--valid-days", dest="valid_days", type=int, help="Validity period for the certificate in days. Default: 365")

    # Boolean encrypt_key flag with tri-state (None == not specified)
    parser.add_argument("--encrypt-key", dest="encrypt_key", action="store_true", help="Encrypt private key with a passphrase (placeholder in code).")
    parser.add_argument("--no-encrypt-key", dest="encrypt_key", action="store_false", help="Do not encrypt private key (default).")

    parser.add_argument("--passphrase", dest="passphrase", help="Passphrase to use when encrypting the private key (if --encrypt-key is set).")

    parser.set_defaults(encrypt_key=None)

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Mode validation helpers
# ---------------------------------------------------------------------------


def _any_dn_cli_set(args: argparse.Namespace) -> bool:
    """
    Return True if any DN-related CLI options were provided.

    Parameters
    ----------
    args:
        Parsed CLI arguments.

    Returns
    -------
    bool
        ``True`` if at least one DN option is non-``None``.
    """
    return any(getattr(args, key) is not None for key in DN_KEYS)


def _any_cfg_cli_set(args: argparse.Namespace) -> bool:
    """
    Return True if any CONFIG-related CLI options were provided.

    Parameters
    ----------
    args:
        Parsed CLI arguments.

    Returns
    -------
    bool
        ``True`` if at least one recognized CONFIG option is non-``None``.
    """
    return any(getattr(args, key, None) is not None for key in CONFIG_DEFAULT)


def _collect_example_mode_conflicts(args: argparse.Namespace) -> list[str]:
    """
    Collect a list of CLI options that conflict with ``--generate-example``.

    Parameters
    ----------
    args:
        Parsed CLI arguments.

    Returns
    -------
    list[str]
        Human-readable descriptions of conflicting options, if any.
    """
    conflicts: list[str] = []

    if args.config:
        conflicts.append("--config")
    if args.config_dir:
        conflicts.append("--config-dir")
    if args.output_dir:
        conflicts.append("--output-dir")
    if _any_dn_cli_set(args):
        conflicts.append("DN CLI options")
    if _any_cfg_cli_set(args):
        conflicts.append("CONFIG CLI options")

    return conflicts


def _validate_example_mode(args: argparse.Namespace) -> None:
    """
    Validate that ``--generate-example`` is not combined with other modes.

    Raises
    ------
    ConfigError
        If any certificate-generation options are used together with
        ``--generate-example``.
    """
    conflicts = _collect_example_mode_conflicts(args)
    if not conflicts:
        return

    conflict_list = ", ".join(conflicts)
    raise ConfigError(f"--generate-example cannot be combined with certificate generation options. Use it alone (optionally with --example-file). Conflicting options: {conflict_list}")


def _validate_standard_mode(args: argparse.Namespace) -> None:
    """
    Validate CLI mode selection when not in example mode.

    Raises
    ------
    ConfigError
        If both ``--config`` and ``--config-dir`` are supplied, or if any
        DN/CONFIG CLI options are used together with ``--config`` or
        ``--config-dir``.
    """
    if args.config and args.config_dir:
        raise ConfigError("--config and --config-dir are mutually exclusive.")

    using_config = bool(args.config or args.config_dir)
    if not using_config:
        return

    if _any_dn_cli_set(args) or _any_cfg_cli_set(args):
        raise ConfigError(
            "DN/CONFIG CLI options cannot be used together with --config or --config-dir. "
            "Choose ONE mode:\n"
            "  * CLI-only: DN/CONFIG via CLI (no --config / --config-dir)\n"
            "  * Config file: --config <file.json>\n"
            "  * Config dir:  --config-dir <dir>"
        )


def validate_mode_constraints(args: argparse.Namespace) -> None:
    """
    Validate that the selected configuration mode and CLI options are compatible.

    Raises
    ------
    ConfigError
        If:
        * Both ``--config`` and ``--config-dir`` are supplied, or
        * Any DN/CONFIG CLI options are used together with ``--config`` or
          ``--config-dir``, or
        * ``--generate-example`` is combined with any certificate-generation
          options (it must be used alone, except for ``--example-file``).
    """
    # Version mode is always allowed alone
    if getattr(args, "version", False):
        return

    # Validate-config must not be combined with other generation modes
    if getattr(args, "validate_config", None) is not None:
        if args.generate_example or args.config_dir or args.config or args.output_dir or _any_dn_cli_set(args) or _any_cfg_cli_set(args):
            raise ConfigError("--validate-config cannot be combined with other generation options. Use it alone to check a single JSON config file.")
        return

    if args.generate_example:
        _validate_example_mode(args)
        return

    _validate_standard_mode(args)


# ---------------------------------------------------------------------------
# Mode processors (no sys.exit here)
# ---------------------------------------------------------------------------


def process_config_dir_mode(config_dir: Path, output_dir: Path | None, passphrase: str | None) -> None:
    """
    Process all JSON configuration files in a directory.

    Parameters
    ----------
    config_dir:
        Directory containing JSON configuration files.
    output_dir:
        Optional base directory for writing certificate artifacts.
    """
    if not config_dir.exists() or not config_dir.is_dir():
        raise ConfigError(f"--config-dir {config_dir} is not a directory.")

    json_files = sorted(config_dir.glob("*.json"))
    if not json_files:
        raise ConfigError(f"No *.json files found in {config_dir}")

    errors = 0

    for cfg_path in json_files:
        try:
            json_dn, json_cfg = load_json_config(cfg_path)
            dn, cfg = merge_settings_json(json_dn, json_cfg)

            # Special case: allow CLI passphrase if JSON omitted it
            if passphrase is not None and "passphrase" not in cfg:
                cfg["passphrase"] = passphrase

            handle_single_cert(dn, cfg, label=str(cfg_path.name), output_dir=output_dir)
        except CertToolError as exc:
            errors += 1
            print(f"ERROR processing {cfg_path}: {exc}", file=sys.stderr)
        except Exception as exc:  # pragma: no cover - defensive
            errors += 1
            print(f"ERROR processing {cfg_path}: unexpected error: {exc}", file=sys.stderr)

    if errors:
        raise CertToolError(f"{errors} config file(s) failed; see error messages above.")


def process_config_file_mode(config_file: Path, output_dir: Path | None, passphrase: str | None) -> None:
    """
    Process a single JSON configuration file.

    Parameters
    ----------
    config_file:
        Path to the JSON configuration file.
    output_dir:
        Optional base directory for writing certificate artifacts.
    """
    if not config_file.exists() or not config_file.is_file():
        raise ConfigError(f"--config {config_file} is not a file.")

    json_dn, json_cfg = load_json_config(config_file)
    dn, cfg = merge_settings_json(json_dn, json_cfg)

    # Special case: allow CLI passphrase if JSON omitted it
    if passphrase is not None and "passphrase" not in cfg:
        cfg["passphrase"] = passphrase

    handle_single_cert(dn, cfg, label=None, output_dir=output_dir)


def process_cli_mode(args: argparse.Namespace, output_dir: Path | None) -> None:
    """
    Process CLI-only mode where DN and CONFIG are provided via flags.

    Parameters
    ----------
    args:
        Parsed CLI arguments.
    output_dir:
        Optional base directory for writing certificate artifacts.
    """
    # Derive DN and CONFIG from CLI flags
    dn: dict[str, Any] = {}
    cfg = dict(CONFIG_DEFAULT)

    # DN from CLI only
    for key in DN_KEYS:
        if hasattr(args, key):
            value = getattr(args, key)
            if value is not None:
                dn[key] = value

    # CONFIG from defaults + CLI
    for key in CONFIG_DEFAULT:
        if hasattr(args, key):
            value = getattr(args, key)
            if value is not None:
                cfg[key] = value

    # Optional passphrase (not part of CONFIG_DEFAULT, but may be provided via CLI)
    if getattr(args, "passphrase", None) is not None:
        cfg["passphrase"] = args.passphrase

    # Ensure types for CONFIG
    cfg["private_key_bits"] = int(cfg["private_key_bits"])
    cfg["valid_days"] = int(cfg["valid_days"])

    if cfg.get("private_key_type", "").upper() != "RSA":
        raise ConfigError(f"Unsupported private_key_type {cfg['private_key_type']!r}; only 'RSA' is supported.")

    # DN must be valid (no defaults)
    validate_dn(dn)

    handle_single_cert(dn, cfg, label=None, output_dir=output_dir)


def inspect_certificate(path: Path) -> None:
    """
    Load and inspect a PEM-encoded certificate, printing key fields.

    Parameters
    ----------
    path:
        Path to a file containing a PEM-encoded X.509 certificate.
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ConfigError(f"Unable to read certificate {path}: {exc}") from exc

    try:
        cert = x509.load_pem_x509_certificate(data)
    except Exception as exc:  # pragma: no cover - defensive
        raise ConfigError(f"Failed to parse certificate {path}: {exc}") from exc

    subject = cert.subject.rfc4514_string()
    issuer = cert.issuer.rfc4514_string()
    not_before = cert.not_valid_before_utc
    not_after = cert.not_valid_after_utc

    print(f"Certificate: {path}")
    print(f"  Subject: {subject}")
    print(f"  Issuer:  {issuer}")
    print(f"  Valid from: {not_before}")
    print(f"  Valid until: {not_after}")

    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    except x509.ExtensionNotFound:
        san = None

    if san is not None:
        dns_names = san.value.get_values_for_type(x509.DNSName)
        if dns_names:
            print(f"  DNS SANs: {', '.join(dns_names)}")


# ---------------------------------------------------------------------------
# Top-level controller
# ---------------------------------------------------------------------------


def run(args: argparse.Namespace) -> None:
    """
    High-level controller for the CLI.

    This function handles:

    * Version reporting (``--version``).
    * Example configuration generation (``--generate-example``).
    * Mode validation for certificate generation.
    * Dispatching to config file / directory / CLI-only processing functions.
    """
    # Version takes precedence and does not require any other validation.
    if getattr(args, "version", False):
        print(get_version())
        return

    # Validate-config mode: JSON parse + merge + DN validation, then exit.
    if getattr(args, "validate_config", None) is not None:
        json_dn, json_cfg = load_json_config(args.validate_config)
        # This will validate DN and private_key_type, etc.
        merge_settings_json(json_dn, json_cfg)
        print(f"Configuration {args.validate_config} is valid.")
        return

    # Inspect-cert mode: print info about an existing PEM certificate.
    if getattr(args, "inspect_cert", None) is not None:
        inspect_certificate(args.inspect_cert)
        return

    # Example mode is validated, then dispatched separately.
    validate_mode_constraints(args)

    if args.generate_example:
        generate_example_config(example_file=args.example_file)
        return

    output_dir = prepare_output_dir(args.output_dir)
    passphrase = getattr(args, "passphrase", None)

    if args.config_dir is not None:
        process_config_dir_mode(args.config_dir, output_dir, passphrase)
    elif args.config is not None:
        process_config_file_mode(args.config, output_dir, passphrase)
    else:
        process_cli_mode(args, output_dir)


def main() -> None:
    """
    CLI entry point.

    Parses command-line arguments, invokes :func:`run`, and converts raised
    exceptions into appropriate exit codes and stderr messages.
    """
    args = parse_args()

    try:
        run(args)
    except CertToolError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Aborted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - defensive
        # Last-resort safety net
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


# EOF
