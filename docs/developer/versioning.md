# Versioning & Release Process

This project follows **Semantic Versioning (SemVer)** with two kinds of pre-releases:

- `-devN` – development snapshots
- `-rcN` – release candidates

All bumps are driven via:

- [`bump-my-version`](https://github.com/callowayproject/bump-my-version) (configured in `pyproject.toml`)
- `make` targets that wrap the common flows
- Git tags (`vX.Y.Z[-suffix]`)

> TL;DR: we use versions like `0.1.1-dev0`, `0.1.1-rc1`, `0.1.1`, and we *never* edit versions by hand — we use `make bump-*`.

---

## Semantic Versioning

We use the standard SemVer pattern with optional pre-release:

```text
MAJOR.MINOR.PATCH[-rcN]
```

Where:

- MAJOR – incompatible API changes
- MINOR – backwards-compatible feature additions
- PATCH – backwards-compatible bug fixes
- -devN – development pre-release for that MAJOR.MINOR.PATCH
- -rcN – release candidate for that MAJOR.MINOR.PATCH

Examples:

- 0.1.0 – initial stable 0.1 release
- 0.1.1-dev0 – start of the 0.1.1 development cycle
- 0.1.1-dev3 – fourth dev snapshot for 0.1.1
- 0.1.1-rc1 – first release candidate for 0.1.1
- 0.1.1 – final 0.1.1 release

We **never** ship 0.1.0-rc1 after a final 0.1.0 is already published. RCs always target the next version (e.g. 0.1.1-rc1 after 0.1.0 is released).

## Version Sources of Truth

The version lives in:

- pyproject.toml → [project].version
- pyproject.toml → [tool.bumpversion].current_version
- src/lupaxa/certtool/version.py → \_\_version\_\_ = "…"

Configuration (simplified) lives under:

```toml
[tool.bumpversion]
current_version = "…"

# Version files updated on every bump
[[tool.bumpversion.files]]
filename = "src/lupaxa/certtool/version.py"
search = '__version__ = "{current_version}"'
replace = '__version__ = "{new_version}"'

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'

[[tool.bumpversion.files]]
filename = "pyproject.toml"
search = 'current_version = "{current_version}"'
replace = 'current_version = "{new_version}"'
```

Every bump creates a Git tag of the form:

```text
vMAJOR.MINOR.PATCH[-rcN]
```

Examples:

- v0.1.1-dev0
- v0.1.1-rc1
- v0.1.1

Tags and commits are created and pushed automatically by bump-my-version (via the hooks configured in pyproject.toml).

## Make Targets (versioning)

Version management is done via make targets that call bump-my-version for you:

> [!IMPORTANT]
>
> - Working tree must be clean (no uncommitted changes).
> - Run on a sensible protected branch (typically master).
> - Don’t edit version.py or pyproject.toml version fields by hand.

### Inspect current version / stage

```bash
make show-version-flow
```

This prints:

- Current version (e.g. 0.1.1-dev3, 0.1.1-rc1, 0.1.1)
- Detected stage: development, release candidate, or final
- Suggested next make bump-* commands

You can also do:

```bash
make version
```

to just print the raw version.

### Final Releases (SemVer bumps)

These bump the final SemVer components. They’re usually used to start a new development cycle.

### Patch release line (e.g. 0.1.0 → 0.1.1-dev0)

From a final release like:

```text
0.1.0
```

run:

```bash
make bump-patch
```

Result (conceptually):

- 0.1.0 → 0.1.1-dev0

Similarly:

### Minor release (e.g. 0.1.1 → 0.2.0-dev0):

```bash
make bump-minor
```

### Major release (e.g. 0.2.0 → 1.0.0-dev0):

```bash
make bump-major
```

Each of these will:

1. Update all version files.
2. Create a commit: Release X.Y.Z-dev0 (or similar).
3. Tag: vX.Y.Z-dev0.
4. Push commit and tag to origin.

You can then continue making changes, bumping dev versions as needed (or just stick with -dev0 until you’re ready for RC).

## RC (release candidate) workflow

RCs use the -rcN suffix:

- First RC: X.Y.Z-rc0
- Subsequent RCs: X.Y.Z-rc1, X.Y.Z-rc2, …

### Promote dev → RC

From a dev build, e.g.:

```text
0.1.1-dev3
```

run:

```bash
make bump-rc
```

This will:

- switch the label from dev → rc
- reset the RC counter to 0
- result in: 0.1.1-rc0
- commit, tag v0.1.1-rc0, and push

If you run make bump-rc again from an RC:

```text
0.1.1-rc0  ->  0.1.1-rc1
0.1.1-rc1  ->  0.1.1-rc2
...
```

### Start RCs directly from a final release

Sometimes you want to skip the explicit -dev phase and go straight to RCs for the next patch.

From:

```text
0.1.0
```

run:

```bash
make bump-rc-patch
```

This will:

1. Bump the patch: 0.1.0 → 0.1.1
2. Switch to RC label and set RC number to 0: 0.1.1 → 0.1.1-rc0
3. Commit, tag v0.1.1-rc0, and push

You can then continue with:

```bash
make bump-rc   # 0.1.1-rc0 -> 0.1.1-rc1, etc.
```

### Finalise RC → Stable

Once the RC is good to go, e.g.:

```text
0.1.1-rc3
```

run:

```bash
make bump-final
```

This:

- drops the -rcN suffix
- produces: 0.1.1
- commits and tags v0.1.1
- pushes to origin

## CI & Publishing

### TestPyPI (pre-release / RC)

RC tags are published to TestPyPI. The workflow is typically triggered by tags matching:

```bash
on:
  push:
    tags:
      - 'v[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+'
```

Typical RC flow:

1. make bump-rc-patch → 0.1.1-rc0 → tag v0.1.1-rc0
2. Push → TestPyPI workflow runs → package published to TestPyPI
3. Optionally iterate with make bump-rc for additional RCs: v0.1.1-rc1, v0.1.1-rc2, …

Typical flow:

1. make bump-rc-patch → 0.1.1-rc1 → tag v0.1.1-rc1
2. Push triggers TestPyPI workflow
3. Verify the package behaves as expected in downstream automation

You can repeat make bump-rc for rc2, rc3, … as needed.

### PyPI (final releases)

Final tags (no -rcN) are published to PyPI. The workflow is typically:

```bash
on:
  push:
    tags:
      - 'v[0-9]+\.[0-9]+\.[0-9]+'
      - '!v[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+'
```

So:

- Tags like v0.1.1 trigger the PyPI publish workflow.
- Tags like v0.1.1-rc1 do not.

## Recommended Release Flow

### New patch release (with RCs)

Assume latest stable is 0.1.0.

1. Make sure everything passes:

```bash
make check-all
```

2. Start patch RC cycle:

```bash
make bump-rc-patch        # 0.1.0 -> 0.1.1-rc1
```

3. Push; let CI / TestPyPI run.
4. If you need more RCs:

```bash
make bump-rc              # 0.1.1-rc1 -> 0.1.1-rc2
```

5. Once you’re happy with the RC:

```bash
make bump-final           # 0.1.1-rcN -> 0.1.1
```

6. CI publishes 0.1.1 to PyPI from tag v0.1.1.

New development cycle after a final

After releasing 0.1.1:

```bash
make bump-patch          # 0.1.1 -> 0.1.2-dev0
# or:
make bump-minor          # 0.1.1 -> 0.2.0-dev0
# or:
make bump-major          # 0.1.1 -> 1.0.0-dev0
```

Then iterate as -devN until you’re ready for RCs (make bump-rc).

## Do & Don’t

Do:

- Run make check-all before any bump.
- Only bump on clean branches.
- Let bump-my-version own commits + tags for version bumps.
- Treat RCs as temporary: they should either become a final or be superseded.

Don’t:

- Manually edit versions in pyproject.toml or version.py except when fixing a mis-sync explicitly.
- Create ad-hoc tags that don’t match the version in the code.
- Reuse the same version number once it has been published to TestPyPI or PyPI.

This document describes the canonical versioning & release process for this project.
If in doubt: use the make bump-* targets instead of manual editing or tagging.
