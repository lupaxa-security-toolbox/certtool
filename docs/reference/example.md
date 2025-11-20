# `lupaxa.certtool.example`

Helpers for generating example configuration files.

## Key Functions

- `build_example_config() -> dict[str, object]`  
  Build an in-memory example JSON configuration structure which includes:

  - A realistic DN
  - Reasonable config defaults
  - Sample `subject_alt_names`
  - Example `passphrase`

- `generate_example_config(example_file: Path | None) -> None`  
  Write the example JSON configuration either to:

  - `stdout` (if `example_file` is `None`), or
  - The specified file, creating parent directories as needed.
