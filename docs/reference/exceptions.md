# `lupaxa.certtool.exceptions`

Custom exception hierarchy for CertTool.

## Base Class

- `CertToolError(Exception)`  
  All tool-specific exceptions derive from this base.

## Subclasses

- `ConfigError(CertToolError)`  
  Raised when CLI or JSON configuration is invalid, inconsistent, or
  missing required fields (e.g. `commonName`).

- `GenerationError(CertToolError)`  
  Raised when cryptographic operations fail, such as key generation,
  CSR creation, certificate signing, or serialization.

- `OutputError(CertToolError)`  
  Raised when output directories or files cannot be created or written.
