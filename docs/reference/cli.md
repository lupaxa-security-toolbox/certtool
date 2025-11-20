# `lupaxa.certtool.cli`

CLI integration and top-level controller.

## Key Functions

- `parse_args() -> argparse.Namespace`  
  Build the `argparse` parser with all CLI options.

- `validate_mode_constraints(args)`  
  Enforce mutual exclusivity between modes and ensure consistent use of
  `--config`, `--config-dir`, `--generate-example`, etc.

- `process_config_dir_mode(config_dir, output_dir, passphrase)`  
  Iterate over all JSON configs in a directory and generate certificates.

- `process_config_file_mode(config_file, output_dir, passphrase)`  
  Process a single JSON config file.

- `process_cli_mode(args, output_dir)`  
  CLI-only mode: merge DN + CONFIG from arguments and generate.

- `run(args: argparse.Namespace) -> None`  
  High-level controller used by both tests and `main()`.

- `main() -> None`  
  Entry point for the `certtool` console script.

## Modes Implemented

- `--version`
- `--generate-example` / `--example-file`
- `--validate-config`
- `--inspect-cert`
- `--config` / `--config-dir`
- DN and CONFIG CLI options
