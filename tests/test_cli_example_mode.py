"""
Tests for the CLI example-generation and version-reporting modes.

This module performs light-weight sanity checks on the behaviour of
:func:`lupaxa.certtool.cli.run` when invoked in:

* ``--generate-example`` mode.
* ``--version`` mode.

The tests avoid spawning subprocesses by constructing a minimal
``argparse.Namespace``-compatible object using :class:`types.SimpleNamespace`.
"""

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import argparse
import json

# ---------------------------------------------------------------------------
# Internal version + CLI entry points
# ---------------------------------------------------------------------------
from lupaxa.certtool import version as get_version  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.cli import run  # pyright: ignore[reportMissingImports]


def _base_args() -> argparse.Namespace:
    """
    Construct a minimal argument namespace with all fields expected by
    :func:`run`, defaulting to a non-generating, non-version mode.
    """
    return argparse.Namespace(
        config=None,
        config_dir=None,
        output_dir=None,
        generate_example=False,
        example_file=None,
        version=False,
        countryName=None,
        stateOrProvinceName=None,
        localityName=None,
        organizationName=None,
        organizationalUnitName=None,
        commonName=None,
        emailAddress=None,
        digest_alg=None,
        private_key_bits=None,
        private_key_type=None,
        valid_days=None,
        encrypt_key=None,
        validate_config=None,
        inspect_cert=None,
        subject_alt_names=None,
        encrypt_password=None,
    )


def test_cli_generate_example_mode_smoke(capsys) -> None:
    """
    Simulate CLI invocation of ``--generate-example`` and verify that JSON
    is printed to stdout and no configuration-related errors are raised.
    """
    args = _base_args()
    args.generate_example = True

    run(args)

    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out, "Expected JSON output from --generate-example mode"

    data = json.loads(out)
    assert "dn" in data
    assert "config" in data


def test_cli_version_flag_prints_version(capsys) -> None:
    """
    Simulate CLI invocation of ``--version`` and assert that the printed
    version string matches the library-reported version.
    """
    args = _base_args()
    args.version = True

    run(args)

    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out == get_version()


# EOF
