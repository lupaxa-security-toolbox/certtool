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
#   make format-diff    # show Ruff format diffs (no writes)
#   make type           # run mypy
#   make test           # run pytest
#   make test-cov       # run pytest with coverage
#   make check          # lint + type + test
#   make check-all      # lint + type + test-cov + audit
#   make audit          # run pip-audit in an isolated venv
#   make bump-*         # bump version via bump2version
#   make docs-build     # build static docs site
#   make docs-serve     # run mkdocs live-reload server
#   make docs-deploy    # run mkdocs gh-deploy --force
#   make build          # build wheel + sdist via hatch
#   make release        # publish via hatch (PyPI config required)
#   make clean          # remove build / cache artefacts

PROJECT_NAME := lupaxa-certtool

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip
BUMP   ?= bump2version
MKDOCS ?= mkdocs

SRC_DIR  := src
TEST_DIR := tests

AUDIT_VENV_DIR := .audit-env
AUDIT_PYTHON   := $(AUDIT_VENV_DIR)/bin/python

.PHONY: \
	audit \
	build \
	bump-major \
	bump-minor \
	bump-patch \
	check \
	check-all \
	check-diff \
	check-diff-all \
	check-style \
	clean \
	docs-build \
	docs-serve \
	docs-deploy \
	format \
	format-diff \
	help \
	install-dev \
	install-test \
	lint \
	release \
	test \
	test-cov \
	type

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help:
	@echo "$(PROJECT_NAME) Makefile"
	@echo
	@echo "Targets:"
	@echo "  install-dev    Editable install with dev extras (.[dev])"
	@echo "  install-test   Editable install with test extras (.[test])"
	@echo
	@echo "  lint           Run Ruff linting + Ruff format --check"
	@echo "  check-style    Run lint + mypy (style & type checks only)"
	@echo "  check-diff     Show Ruff lint diffs (ruff check --diff)"
	@echo "  check-diff-all Show Ruff lint + format diffs"
	@echo "  format         Run Ruff formatter (auto-format)"
	@echo "  format-diff    Show Ruff format diffs (ruff format --diff)"
	@echo "  type           Run mypy type checking"
	@echo
	@echo "  test           Run pytest"
	@echo "  test-cov       Run pytest with coverage"
	@echo "  check          Run lint, type, and test"
	@echo "  check-all      Run lint, type, test, coverage, and audit"
	@echo
	@echo "  audit          Run pip-audit in a temporary venv"
	@echo
	@echo "  docs-build     Build static MkDocs documentation"
	@echo "  docs-serve     Serve MkDocs documentation (live reload)"
	@echo "  docs-deploy    Publish docs to GitHub Pages"
	@echo
	@echo "  bump-patch     Bump patch version via bump2version"
	@echo "  bump-minor     Bump minor version via bump2version"
	@echo "  bump-major     Bump major version via bump2version"
	@echo
	@echo "  build          Build distributions via hatch"
	@echo "  release        Publish distributions via hatch publish"
	@echo "  clean          Remove build, cache artefacts, and audit venv"

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

docs-deploy:
	$(MKDOCS) gh-deploy --clean --force

# ---------------------------------------------------------------------------
# Versioning & Packaging
# ---------------------------------------------------------------------------

bump-patch:
	$(BUMP) patch

bump-minor:
	$(BUMP) minor

bump-major:
	$(BUMP) major

build:
	hatch build

release: build
	hatch publish

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
