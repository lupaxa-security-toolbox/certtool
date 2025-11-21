# Versioning & Release Process

This project uses **Semantic Versioning (SemVer)** with optional **pre-release
suffixes** for development and release candidate builds.

We keep things intentionally simple and script-driven via `make` targets.

## Version Formats

All versions follow:

```text
MAJOR.MINOR.PATCH[-devN | -rcN]
```

Where:

- MAJOR – incompatible / breaking changes
- MINOR – backwards-compatible feature additions
- PATCH – backwards-compatible bug fixes
- Optional -devN – development snapshots for a given version
- Optional -rcN – release candidates for a given version

Examples:

- 0.1.0 – stable release
- 0.1.1-dev1 – first dev snapshot for the upcoming 0.1.1
- 0.1.1-dev2 – second dev snapshot for the same target
- 0.1.1-rc1 – first release candidate for 0.1.1
- 0.1.1 – final 0.1.1 release

At any point in time, one of these should be true:

- You are on a stable version: X.Y.Z
- You are iterating on dev snapshots: X.Y.Z-devN
- You are iterating on release candidates: X.Y.Z-rcN

## Version Sources of Truth

The version is stored in:

- pyproject.toml → [project].version
- pyproject.toml → [tool.bumpversion].current_version
- src/lupaxa/certtool/version.py → \_\_version\_\_ = "…"

Those are kept in sync by the version bump tools and make targets.
You should never edit them by hand unless you are repairing a broken state.

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

## High-level bumping rules

The project uses a small set of make targets that encapsulate all the logic.
Conceptually, they behave as follows:

1. Base SemVer bumps (no pre-release suffix):
    - bump-patch : X.Y.Z → X.Y.(Z+1)
    - bump-minor : X.Y.Z → X.(Y+1).0
    - bump-major : X.Y.Z → (X+1).0.0

2. Development snapshots:

Use this when you want to mark “work in progress” snapshots but don’t want
to commit to an RC yet.

```bash
make bump-dev
```

Behaviour:

- If current version is stable:
  - X.Y.Z → X.Y.(Z+1)-dev1
- If current version is already dev:
  - X.Y.Z-devN → X.Y.Z-dev(N+1)
- If current version is rc:
  - X.Y.Z-rcN → error (you should either go to final or bump the patch first)

3. Release candidates:

Use this when you think the change set is “release-shaped” and you want
something candidates can be tested against (CI, TestPyPI, etc.).

```bash
make bump-rc
```

Behaviour:

- If current version is dev:
  - X.Y.Z-devN → X.Y.Z-rc1
(drops the dev suffix and starts RCs for that same version)
- If current version is rc:
  - X.Y.Z-rcN → X.Y.Z-rc(N+1)
- If current version is stable:
  - X.Y.Z → X.Y.(Z+1)-rc1 (bumps patch and starts RCs for the next patch)

4. Final releases:

Use this when you are confident an RC (or dev snapshot) is now a true release.

```bash
make bump-final
```

Behaviour:

- If current version is X.Y.Z-rcN → X.Y.Z
  - (drops the RC suffix and finalises the version)
- If current version is X.Y.Z-devN → X.Y.Z
  - (drops the dev suffix and finalises, though this should be rare in practice)
- If current version is already X.Y.Z → no-op / error

## Make targets summary

These are the version-related make targets and what they mean:

```bash
# Pure SemVer bumps (no -dev/-rc added automatically)
make bump-patch     # X.Y.Z       -> X.Y.(Z+1)
make bump-minor     # X.Y.Z       -> X.(Y+1).0
make bump-major     # X.Y.Z       -> (X+1).0.0

# Development pre-releases
make bump-dev       # X.Y.Z       -> X.Y.(Z+1)-dev1
                    # X.Y.Z-devN  -> X.Y.Z-dev(N+1)

# Release candidates
make bump-rc        # X.Y.Z-devN  -> X.Y.Z-rc1
                    # X.Y.Z-rcN   -> X.Y.Z-rc(N+1)
                    # X.Y.Z       -> X.Y.(Z+1)-rc1

# Finalisation
make bump-final     # X.Y.Z-rcN   -> X.Y.Z
                    # X.Y.Z-devN  -> X.Y.Z
```

> [!NOTE]
>
> Implementation detail:
> Under the hood we use bump-my-version for the core MAJOR.MINOR.PATCH
> bumping, and lightweight text editing for the -devN / -rcN suffixes.
> You don’t need to call bump-my-version directly - always go via make.

## Typical flows

1. Tiny patch, no pre-releases

For a very small / low-risk change where you’re happy to ship directly:

```bash
make check-all      # lint, types, tests, coverage
make bump-patch     # 0.1.0 -> 0.1.1
git push --tags     # if not already pushed by the tooling
```

CI will treat 0.1.1 as a standard release (e.g. publish to PyPI if configured).

2. Normal patch with dev + RC

Assume latest stable is 0.1.0 and you’re starting work on 0.1.1:

```bash
# 1) Start dev cycle
make bump-dev       # 0.1.0 -> 0.1.1-dev1

# 2) Iterate as much as you like
#    (code, commit, repeat; optionally bump to dev2, dev3, ...)
make bump-dev       # 0.1.1-dev1 -> 0.1.1-dev2

# 3) When it feels like a candidate, promote to RC
make bump-rc        # 0.1.1-devN -> 0.1.1-rc1

# 4) If you need more RCs
make bump-rc        # 0.1.1-rc1 -> 0.1.1-rc2

# 5) When done, finalise
make bump-final     # 0.1.1-rcN -> 0.1.1
```

3. Jump straight to RC from a stable

If you’re coming from a stable release and want to go directly to an RC
(without an explicit -dev phase):

```bash
# From 0.1.0:
make bump-rc        # 0.1.0 -> 0.1.1-rc1
```

Then proceed with more bump-rc and finally bump-final as above.

## Do & Don’t

Do:

- Run make check-all before any version bump.
- Keep the working tree clean before calling any make bump-* target.
- Let the make targets manipulate the version fields; don’t hand-edit them.
- Use dev builds for “ongoing work”, RC builds for “ready to test”.

Don’t:

- Manually tweak pyproject.toml or version.py unless you are fixing a clearly broken state.
- Reuse a version number once it has been pushed / released (even to TestPyPI).
- Push tags that don’t match the version stored in the code.

If in doubt: **run make show-version-flow** (if present in this repo) or
look at the current version string and follow the patterns in this document.
