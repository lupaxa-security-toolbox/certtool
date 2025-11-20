"""
Custom exception types for the Lupaxa certificate generation library.

These provide a small hierarchy that callers can use to distinguish between
configuration, generation, and output-related failures, or catch the common
base class for all expected errors.
"""


class CertToolError(Exception):
    """
    Base exception for all certificate tool errors.

    This serves as a common ancestor for all custom exceptions in this
    package, allowing callers to catch a single type for all expected
    error conditions originating from configuration, generation, or
    output handling.
    """


class ConfigError(CertToolError):
    """
    Raised when invalid configuration or mode selection is detected.

    Typical causes include:

    * Invalid or missing values in configuration dictionaries or JSON files.
    * Unsupported digest algorithms or private key types.
    * Missing required DN attributes (for example, ``"commonName"``).
    """


class GenerationError(CertToolError):
    """
    Raised when a failure occurs during key, CSR, or certificate generation.

    This may wrap low-level exceptions from the :mod:`cryptography` library,
    such as:

    * Failures in RSA key generation.
    * Errors during CSR or certificate signing operations.
    """


class OutputError(CertToolError):
    """
    Raised when writing output files or creating directories fails.

    Typical causes include:

    * Filesystem permission issues.
    * Non-writable or non-existent parent directories.
    * Collisions or failures when creating per-certificate directories.
    """


# EOF
