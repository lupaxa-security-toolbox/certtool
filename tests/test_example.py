"""
Tests for the example configuration helpers.

This module verifies that:

* :func:`lupaxa.certtool.build_example_config` returns a structurally valid
  configuration dictionary with reasonable defaults.
* :func:`lupaxa.certtool.generate_example_config` can emit the example
  configuration both to stdout and to a file on disk.
"""

# ---------------------------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------------------------
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Internal certificate generation helpers
# ---------------------------------------------------------------------------
from lupaxa.certtool import build_example_config, generate_example_config  # pyright: ignore[reportMissingImports]


def test_build_example_config_has_dn_and_config() -> None:
    """
    Ensure the example configuration contains both ``dn`` and ``config`` keys
    with sensible values and types.

    This test performs basic sanity checks rather than attempting to exhaustively
    validate every field; the goal is to catch obvious regressions in the
    structure of the example config.
    """
    cfg = build_example_config()

    assert "dn" in cfg
    assert "config" in cfg

    dn = cfg["dn"]
    conf = cfg["config"]

    # DN sanity checks
    assert dn["commonName"]
    assert dn["countryName"]
    assert dn["organizationName"]

    # Config sanity checks
    assert conf["digest_alg"] in {"sha256", "sha384", "sha512"}
    assert conf["private_key_bits"] >= 2048
    assert conf["private_key_type"].upper() == "RSA"
    assert isinstance(conf["encrypt_key"], bool)
    assert conf["valid_days"] > 0


def test_generate_example_config_writes_to_stdout(capsys) -> None:
    """
    Verify that :func:`generate_example_config` prints JSON to stdout when
    no target file is supplied.

    The output is parsed back as JSON to ensure that it is syntactically valid
    and structurally similar to the result of :func:`build_example_config`.
    """
    generate_example_config(example_file=None)

    captured = capsys.readouterr()
    out = captured.out.strip()
    assert out, "Expected some JSON output on stdout"

    data = json.loads(out)
    assert "dn" in data
    assert "config" in data


def test_generate_example_config_writes_to_file(tmp_path: Path) -> None:
    """
    Ensure that :func:`generate_example_config` can write to a file when an
    output path is provided.

    The resulting file is parsed as JSON to confirm that it contains a valid
    example configuration.
    """
    target = tmp_path / "example-cert.json"

    generate_example_config(example_file=target)

    assert target.exists()
    content = target.read_text(encoding="utf-8")
    data = json.loads(content)
    assert "dn" in data
    assert "config" in data

# EOF
