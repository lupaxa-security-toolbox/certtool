# Makefile for lupaxa-certtool
#
# Common workflows:
#   make install-dev    # editable install with dev extras
#   make install-test   # editable install with test extras
#   make lint           # run Ruff lint + Ruff format --check
#   make check-style    # run lint + mypy (style & type)
#   make check-diff     # show Ruff lint diffs (no writes)
#   make check-diff-all # show Ruff lint + format diffs
#   make format         # auto-format with Ruff
#   make format-diff    # show Ruff format diffs (ruff format --diff)
#   make type           # run mypy
#   make test           # run pytest
#   make test-cov       # run pytest with coverage
#   make check          # run lint + type + test
#   make check-all      # run lint + type + test-cov + audit
#   make audit          # run pip-audit in an isolated venv
#   make bump-*         # bump version via bump-my-version (incl. RC helpers)
#   make docs-build     # build static docs site
#   make docs-serve     # run mkdocs live-reload server
#   make build          # build wheel + sdist via hatch
#   make release        # publish via hatch (PyPI config required)
#   make clean          # remove build / cache artefacts
#   make version        # show current project version

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
	@echo "  install-dev     Editable install with dev extras (.[dev])"
	@echo "  install-test    Editable install with test extras (.[test])"
	@echo
	@echo "  lint            Run Ruff linting + Ruff format --check"
	@echo "  check-style     Run lint + mypy (style & type checks only)"
	@echo "  check-diff      Show Ruff lint diffs (ruff check --diff)"
	@echo "  check-diff-all  Show Ruff lint + format diffs"
	@echo "  format          Run Ruff formatter (auto-format)"
	@echo "  format-diff     Show Ruff format diffs (ruff format --diff)"
	@echo "  type            Run mypy type checking"
	@echo
	@echo "  test            Run pytest"
	@echo "  test-cov        Run pytest with coverage"
	@echo "  check           Run lint, type, and test"
	@echo "  check-all       Run lint, type, test, coverage, and audit"
	@echo
	@echo "  audit           Run pip-audit in a temporary venv"
	@echo
	@echo "  docs-build      Build static MkDocs documentation"
	@echo "  docs-serve      Serve MkDocs documentation (live reload)"
	@echo
	@echo "  bump-patch      Bump patch version (final release)"
	@echo "  bump-minor      Bump minor version (final release)"
	@echo "  bump-major      Bump major version (final release)"
	@echo "  bump-rc         Bump RC build number (e.g. 0.1.0-rc2 -> 0.1.0-rc3)"
	@echo "  bump-rc-patch   Bump to next patch as RC (e.g. 0.1.0 -> 0.1.1-rc0)"
	@echo "  bump-final      Drop RC suffix for final release (e.g. 0.1.0-rc3 -> 0.1.0)"
	@echo
	@echo "  build           Build distributions via hatch"
	@echo "  release         Publish distributions via hatch publish"
	@echo "  version         Show current project version (from pyproject.toml)"
	@echo "  clean           Remove build, cache artefacts, and audit venv"

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
# NOTE:
#   Uses bump-my-version, which reads [tool.bumpversion] from pyproject.toml
#   and supports SemVer + rc pre-releases via pre_l / pre_n.

bump-patch:
	$(BUMP) bump patch

bump-minor:
	$(BUMP) bump minor

bump-major:
	$(BUMP) bump major

# Bump current RC build number: 0.1.0-rc2 -> 0.1.0-rc3
bump-rc:
	$(BUMP) bump pre_n

# Start next patch line as RC (e.g. 0.1.0 -> 0.1.1-rc0)
# This assumes the SemVer+pre_l flow from the bump-my-version docs.
bump-rc-patch:
	$(BUMP) bump patch
	$(BUMP) bump pre_l

# Finalize an RC release: 0.1.0-rc3 -> 0.1.0
bump-final:
	$(BUMP) bump pre_l

build:
	hatch build

release: build
	hatch publish

# Show current version from pyproject.toml
version:
	@echo "$(PROJECT_NAME) version: $(PROJECT_VERSION)"

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
