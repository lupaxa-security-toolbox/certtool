# Versioning & Release Process

This project follows **Semantic Versioning (SemVer)** with **RC (release candidate) pre-releases** and a small set of `make` targets to automate version bumps, tagging, and publishing.

> TL;DR: we use versions like `0.1.0`, `0.1.1-rc1`, `0.1.1`, and drive them via `bump-my-version` and Git tags.

---

## Semantic Versioning

We use the standard SemVer pattern:

```text
MAJOR.MINOR.PATCH[-rcN]
```

Where:

- MAJOR – incompatible API changes
- MINOR – backwards-compatible feature additions
- PATCH – backwards-compatible bug fixes
- Optional -rcN – pre-release (“release candidate”) for a given MAJOR.MINOR.PATCH (e.g. 0.1.1-rc1, 0.1.1-rc2)

Examples:

- 0.1.0 – initial stable 0.1 release
- 0.1.1-rc1 – first release candidate for 0.1.1
- 0.1.1 – final 0.1.1 release

We never ship 0.1.0-rc1 after a final 0.1.0 is already published. RCs are always for the next version (e.g. 0.1.1-rc1 after 0.1.0).

## Version Sources of Truth

The version lives in:

- pyproject.toml → [project].version
- pyproject.toml → [tool.bumpversion].current_version
- src/lupaxa/certtool/version.py → \_\_version\_\_ = "…"

These are kept in sync automatically by bump-my-version, configured under:

```toml
[tool.bumpversion]
...
[[tool.bumpversion.files]]
filename = "src/lupaxa/certtool/version.py"
...
[[tool.bumpversion.files]]
filename = "pyproject.toml"
...
```

We also create a Git tag for every version in the form:

```text
vMAJOR.MINOR.PATCH[-rcN]
```

Examples:

- v0.1.0
- v0.1.1-rc1
- v0.1.1

Tags are created automatically by bump-my-version and pushed to GitHub.

## Make Targets (versioning)

All version bumps are done via make targets which delegate to bump-my-version.

> [!IMPORTANT]
> Pre-condition: the working tree must be clean and on a sensible branch (typically master).
> We intentionally run with allow_dirty = false.

### Final releases

These bump the final SemVer (no -rcN):

### Patch release (e.g. 0.1.0 → 0.1.1):

```bash
make bump-patch
```

### Minor release (e.g. 0.1.1 → 0.2.0):

```bash
make bump-minor
```

### Major release (e.g. 0.2.0 → 1.0.0):

```bash
make bump-major
```

Each of these will:

1. Update pyproject.toml and version.py
2. Create a commit: Release X.Y.Z
3. Tag: vX.Y.Z
4. Push commit and tag to origin

## RC (release candidate) workflow

RCs use the SemVer pre-release part: -rcN.

### Bump RC number

From:

```text
0.1.0-rc1
```

to:

```text
0.1.0-rc2
```

Use:

```bash
make bump-rc
```

This runs:

```bash
bump-my-version bump pre_n
```

and will:

- Increment the RC number (rc1 → rc2)
- Commit and tag (v0.1.0-rc2)
- Push changes to origin

### Start RCs for the next patch

From a final version:

```text
0.1.0
```

to the first RC of the next patch:

```text
0.1.1-rc1
```

Use:

```bash
make bump-rc-patch
```

Which internally does:

```bash
bump-my-version bump patch   # 0.1.0 -> 0.1.1
bump-my-version bump pre_l   # 0.1.1 -> 0.1.1-rc1
```

Again, this updates files, commits, tags (v0.1.1-rc1), and pushes.

### Finalise an RC to a stable release

From:

```text
0.1.1-rc3
```

to:

```text
0.1.1
```

Use:

```bash
make bump-final
```

Which runs:

```bash
bump-my-version bump pre_l
```

This drops the rc label (and the RC number), producing the final SemVer:

- File versions → 0.1.1
- Tag → v0.1.1
- Commit + tag pushed

## CI & Publishing

### TestPyPI (pre-release / RC)

We publish RC builds to TestPyPI from tags that match:

```bash
on:
  push:
    tags:
      - 'v[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+'
```

Typical flow:

1. make bump-rc-patch → 0.1.1-rc1 → tag v0.1.1-rc1
2. Push triggers TestPyPI workflow
3. Verify the package behaves as expected in downstream automation

You can repeat make bump-rc for rc2, rc3, … as needed.

### PyPI (final releases)

We publish final releases to PyPI from tags that match:

```bash
on:
  push:
    tags:
      - 'v[0-9]+\.[0-9]+\.[0-9]+'
      - '!v[0-9]+\.[0-9]+\.[0-9]+-rc[0-9]+'
```

So any tag like v0.1.1 will:

1. Build the sdist + wheel
2. Use trusted publishing to upload to PyPI

RC tags (-rcN) are explicitly excluded from PyPI.

## Recommended Release Flow

### New patch release (with RCs)

Assume latest stable is 0.1.0.

1. Ensure working tree is clean, tests pass:

```bash
make check-all
```

2. Start RC for the next patch:

```bash
make bump-rc-patch        # 0.1.0 -> 0.1.1-rc1
```

3. Let CI run, including TestPyPI publish.
4. If you need another iteration:

```bash
make bump-rc              # 0.1.1-rc1 -> 0.1.1-rc2
```

5. Once you’re happy with the RC:

```bash
make bump-final           # 0.1.1-rcN -> 0.1.1
```

6. CI publishes 0.1.1 to PyPI from tag v0.1.1.

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
