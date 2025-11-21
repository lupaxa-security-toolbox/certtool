"""
Version information for the ``lupaxa.certtool`` package.

This module provides a single source of truth for the runtime version that is
used by both the library API and the command-line interface.
"""

from __future__ import annotations

#: The package version, kept in sync with ``pyproject.toml``.
__version__ = "0.1.1-rc1"


def get_version() -> str:
    """
    Return the current version of the ``lupaxa.certtool`` package.

    Returns
    -------
    str
        The version string, for example ``"0.1.0"``.
    """
    return __version__


# EOF
