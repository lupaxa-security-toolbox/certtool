"""
Tests for version helpers in the ``lupaxa.certtool`` package.

This module verifies that:

* The public :func:`lupaxa.certtool.version` helper returns a non-empty string.
* The public helper is consistent with the internal
  :func:`lupaxa.certtool.version.get_version` implementation.
"""

# ---------------------------------------------------------------------------
# Internal version exports
# ---------------------------------------------------------------------------
from lupaxa.certtool import version as public_version  # pyright: ignore[reportMissingImports]
from lupaxa.certtool.version import get_version  # pyright: ignore[reportMissingImports]


def test_public_version_is_non_empty_string() -> None:
    """
    Ensure that the public :func:`lupaxa.certtool.version` helper returns a
    non-empty string.

    This is a basic sanity check to catch accidental ``None`` or empty
    assignments and to verify that the function is callable.
    """
    value = public_version()
    assert isinstance(value, str)
    assert value.strip() != ""


def test_public_and_internal_version_match() -> None:
    """
    Verify that the public :func:`lupaxa.certtool.version` helper is consistent
    with the internal :func:`lupaxa.certtool.version.get_version` function.

    This guards against accidental divergence between the re-exported helper
    and the underlying implementation in :mod:`lupaxa.certtool.version`.
    """
    assert public_version() == get_version()  # nosec B101

# EOF
