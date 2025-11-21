# Makefile for lupaxa-certtool
#
# Common workflows:
#   make install-dev       # editable install with dev extras
#   make install-test      # editable install with test extras
#   make lint              # run Ruff lint + Ruff format --check
#   make check-style       # run lint + mypy (style & type)
#   make check-diff        # show Ruff lint diffs (no writes)
#   make check-diff-all    # show Ruff lint + format diffs
#   make format            # auto-format with Ruff
#   make format-diff       # show Ruff format diffs (ruff format --diff)
#   make type              # run mypy
#   make test              # run pytest
#   make test-cov          # run pytest with coverage
#   make check             # run lint + type + test
#   make check-all         # run lint + type + test-cov + audit
#   make audit             # run pip-audit in an isolated venv
#   make bump-*            # bump version via bump-my-version (incl. dev/RC helpers)
#   make docs-build        # build static docs site
#   make docs-serve        # run mkdocs live-reload server
#   make build             # build wheel + sdist via hatch
#   make release           # publish via hatch (PyPI config required)
#   make clean             # remove build / cache artefacts
#   make version           # show current project version
#   make show-version-flow # show version stage + suggested next commands

PROJECT_NAME := lupaxa-certtool

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip
BUMP   ?= bump-my-version
MKDOCS ?= mkdocs

SRC_DIR  := src
TEST_DIR := tests

AUDIT_VENV_DIR := .audit-env
AUDIT_PYTHON   := $(AUDIT_VENV_DIR)/bin/python

# Extract the current version from pyproject.toml ([project] section)
PROJECT_VERSION := $(shell sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml | head -n1)

.PHONY: \
	audit \
	build \
	bump-major \
	bump-minor \
	bump-patch \
	bump-rc \
	bump-rc-patch \
	bump-final \
	check \
	check-all \
	check-diff \
	check-diff-all \
	check-style \
	clean \
	docs-build \
	docs-serve \
	format \
	format-diff \
	help \
	install-dev \
	install-test \
	lint \
	release \
	show-version-flow \
	test \
	test-cov \
	type \
	version

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help:
	@echo "$(PROJECT_NAME) Makefile"
	@echo
	@echo "Targets:"
	@echo "  install-dev         Editable install with dev extras (.[dev])"
	@echo "  install-test        Editable install with test extras (.[test])"
	@echo
	@echo "  lint                Run Ruff linting + Ruff format --check"
	@echo "  check-style         Run lint + mypy (style & type checks only)"
	@echo "  check-diff          Show Ruff lint diffs (ruff check --diff)"
	@echo "  check-diff-all      Show Ruff lint + format diffs"
	@echo "  format              Run Ruff formatter (auto-format)"
	@echo "  format-diff         Show Ruff format diffs (ruff format --diff)"
	@echo "  type                Run mypy type checking"
	@echo
	@echo "  test                Run pytest"
	@echo "  test-cov            Run pytest with coverage"
	@echo "  check               Run lint, type, and test"
	@echo "  check-all           Run lint, type, test, coverage, and audit"
	@echo
	@echo "  audit               Run pip-audit in a temporary venv"
	@echo
	@echo "  docs-build          Build static MkDocs documentation"
	@echo "  docs-serve          Serve MkDocs documentation (live reload)"
	@echo
	@echo "  bump-patch          Bump patch (SemVer) – usually starts next dev cycle"
	@echo "  bump-minor          Bump minor version (SemVer)"
	@echo "  bump-major          Bump major version (SemVer)"
	@echo "  bump-rc             Promote dev -> rc0, or rcN -> rc(N+1)"
	@echo "  bump-rc-patch       Start next patch directly as rc0 (skips dev)"
	@echo "  bump-final          Finalize RC: rcN -> final (drop pre-release)"
	@echo
	@echo "  version             Show current project version"
	@echo "  show-version-flow   Show stage (dev/rc/final) + suggested next steps"
	@echo "  build               Build distributions via hatch"
	@echo "  release             Publish distributions via hatch publish"
	@echo "  clean               Remove build, cache artefacts, and audit venv"

# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

install-dev:
	$(PIP) install -e ".[dev]"

install-test:
	$(PIP) install -e ".[test]"

# ---------------------------------------------------------------------------
# Linting / Style / Types
# ---------------------------------------------------------------------------

lint:
	ruff check $(SRC_DIR) $(TEST_DIR)
	ruff format --check $(SRC_DIR) $(TEST_DIR)

check-style: lint type

check-diff:
	ruff check --diff $(SRC_DIR) $(TEST_DIR)

check-diff-all: check-diff format-diff

type:
	mypy $(SRC_DIR)

format:
	ruff format $(SRC_DIR) $(TEST_DIR)

format-diff:
	ruff format --diff $(SRC_DIR) $(TEST_DIR)

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test:
	pytest

test-cov:
	pytest --cov=lupaxa.certtool --cov-report=term-missing

check: lint type test

check-all: lint type test-cov audit

# ---------------------------------------------------------------------------
# Security / Dependency Audit
# ---------------------------------------------------------------------------

audit:
	@echo "==> Creating temporary audit venv: $(AUDIT_VENV_DIR)"
	rm -rf $(AUDIT_VENV_DIR)
	$(PYTHON) -m venv $(AUDIT_VENV_DIR)
	$(AUDIT_PYTHON) -m pip install --upgrade pip
	$(AUDIT_PYTHON) -m pip install -e ".[dev]"
	@echo "==> Running pip-audit inside $(AUDIT_VENV_DIR)"
	$(AUDIT_PYTHON) -m pip_audit
	@echo "==> Removing audit venv"
	rm -rf $(AUDIT_VENV_DIR)

# ---------------------------------------------------------------------------
# Documentation (MkDocs)
# ---------------------------------------------------------------------------

docs-build:
	$(MKDOCS) build

docs-serve:
	$(MKDOCS) serve

# ---------------------------------------------------------------------------
# Versioning & Packaging
# ---------------------------------------------------------------------------
# Uses bump-my-version with [tool.bumpversion] in pyproject.toml
# SemVer + pre-release via pre_l / pre_n:
#   X.Y.Z-devN  -> development builds
#   X.Y.Z-rcN   -> release candidates
#   X.Y.Z       -> final

bump-patch:
	$(BUMP) bump patch

bump-minor:
	$(BUMP) bump minor

bump-major:
	$(BUMP) bump major

# Promote dev -> rc0, or bump rcN -> rc(N+1)
bump-rc:
	@if echo "$(PROJECT_VERSION)" | grep -q -- "-dev"; then \
		echo "Promoting dev to rc0 from $(PROJECT_VERSION)"; \
		$(BUMP) bump pre_l --new-version rc; \
		$(BUMP) bump pre_n --new-version 0; \
	else \
		echo "Bumping existing rc pre_n from $(PROJECT_VERSION)"; \
		$(BUMP) bump pre_n; \
	fi

# Start next patch as rc0 directly (e.g. 0.1.0 -> 0.1.1-rc0)
bump-rc-patch:
	$(BUMP) bump patch
	$(BUMP) bump pre_l --new-version rc
	$(BUMP) bump pre_n --new-version 0

# Finalize an RC release: X.Y.Z-rcN -> X.Y.Z (drop pre-release)
bump-final:
	@if ! echo "$(PROJECT_VERSION)" | grep -q -- "-rc[0-9]\+"; then \
		echo "ERROR: bump-final can only be run from an -rcN version (current: $(PROJECT_VERSION))" >&2; \
		exit 1; \
	fi; \
	echo "Finalizing RC to stable from $(PROJECT_VERSION)"; \
	$(BUMP) bump pre_l

build:
	hatch build

release: build
	hatch publish

# Show current version from pyproject.toml
version:
	@echo "$(PROJECT_NAME) version: $(PROJECT_VERSION)"

# Show the current stage + suggested flow
show-version-flow:
	@echo "Current version: $(PROJECT_VERSION)"
	@if echo "$(PROJECT_VERSION)" | grep -q -- "-dev"; then \
		echo "Stage: development pre-release"; \
		echo "Suggested next steps:"; \
		echo "  - make bump-rc        # promote to first RC (0.1.x-rc0)"; \
		echo "  - or keep iterating at devN"; \
	elif echo "$(PROJECT_VERSION)" | grep -q -- "-rc"; then \
		echo "Stage: release candidate"; \
		echo "Suggested next steps:"; \
		echo "  - make bump-rc        # bump to next RC if needed"; \
		echo "  - make bump-final     # finalize as stable release"; \
	else \
		echo "Stage: final / stable release"; \
		echo "Suggested next steps:"; \
		echo "  - make bump-patch     # start next patch dev cycle (X.Y.(Z+1)-dev0)"; \
		echo "  - make bump-minor     # start next minor dev cycle (X.(Y+1).0-dev0)"; \
		echo "  - make bump-major     # start next major dev cycle ((X+1).0.0-dev0)"; \
	fi

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	rm -rf \
		$(AUDIT_VENV_DIR) \
		dist \
		build \
		*.egg-info \
		.pytest_cache \
		.mypy_cache \
		.ruff_cache
