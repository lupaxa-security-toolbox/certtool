"""
Lupaxa certificate generation package.

This package exposes both:

* A programmatic API for generating self-signed certificates, CSRs, and keys.
* A command-line interface, via :mod:`lupaxa.certtool.cli`.
* Utilities for loading/merging configuration and generating example configs.

Most users will interact with the CLI entry point (for example, ``certtool``),
but library consumers can import :mod:`lupaxa.certtool.certs`,
:mod:`lupaxa.certtool.config`, and :mod:`lupaxa.certtool.example` directly,
or use the shortcuts re-exported here.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Public certificate-generation API (.certs)
# ---------------------------------------------------------------------------
from .certs import (
    PemBundle,
    generate_from_dn_and_config,
    generate_from_json_file,
)

# ---------------------------------------------------------------------------
# Example configuration generators (.example)
# ---------------------------------------------------------------------------
from .example import (
    build_example_config,
    generate_example_config,
)

# ---------------------------------------------------------------------------
# Exceptions for callers to catch (.exceptions)
# ---------------------------------------------------------------------------
from .exceptions import (
    CertToolError,
    ConfigError,
    GenerationError,
    OutputError,
)

# ---------------------------------------------------------------------------
# Shared configuration constants (.utils)
# ---------------------------------------------------------------------------
from .utils import (
    CONFIG_DEFAULT,
    DN_KEYS,
)

# ---------------------------------------------------------------------------
# Version information (.version)
# ---------------------------------------------------------------------------
from .version import get_version as version

# ---------------------------------------------------------------------------
# Public re-export list
# ---------------------------------------------------------------------------
__all__ = [
    # Exceptions
    "CertToolError",
    "ConfigError",
    "GenerationError",
    "OutputError",
    # Shared config
    "DN_KEYS",
    "CONFIG_DEFAULT",
    # Programmatic certificate-generation API
    "PemBundle",
    "generate_from_json_file",
    "generate_from_dn_and_config",
    # Example configuration helpers
    "build_example_config",
    "generate_example_config",
    # Version information
    "version",
]


# EOF
