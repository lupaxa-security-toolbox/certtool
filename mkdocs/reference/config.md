# `lupaxa.certtool.config`

Configuration loading and validation helpers.

## Key Functions

- `load_json_config(path: Path) -> tuple[dict[str, object], dict[str, object]]`  
  Load DN/CONFIG from a JSON file. Supports both:

  - Explicit `{"dn": {...}, "config": {...}}`
  - Flat dictionaries, where keys are split between DN and CONFIG.

- `validate_dn(dn: dict[str, object]) -> None`  
  Ensure that DN is usable:

  - Requires at least a non-empty `commonName`
  - Raises `ConfigError` on invalid DN.

- `merge_settings_cli(args) -> tuple[dict[str, object], dict[str, object]]`  
  CLI-only mode: derive DN and CONFIG from CLI arguments and defaults.

- `merge_settings_json(json_dn, json_cfg) -> tuple[dict[str, object], dict[str, object]]`  
  JSON-based modes: merge JSON DN/CONFIG with defaults and validate.
