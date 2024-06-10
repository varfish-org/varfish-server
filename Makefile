# Top-Level Makefile

# Set the shell to bash with printing of all commands (`-x`) and unofficial
# strict mode (`-euo pipefail`).
SHELL := bash -x -euo pipefail

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Targets:"
	@echo "  help    This help (default target)"
	@echo "  deps    Install all dependencies"
	@echo "  format  Format source code"
	@echo "  lint    Run lint checks"
	@echo "  test    Run tests"
	@echo "  ci      Install dependencies, run lints and tests"
	@echo "  docs    Generate the documentation"

.PHONY: deps
deps:
	$(MAKE) -C backend deps
	$(MAKE) -C frontend deps

.PHONY: format
format:
	$(MAKE) -C backend format
	$(MAKE) -C frontend format

.PHONY: lint
lint:
	$(MAKE) -C backend lint
	$(MAKE) -C frontend lint

.PHONY: test
test:
	$(MAKE) -C backend test
	$(MAKE) -C frontend test

.PHONY: ci
ci:
	$(MAKE) -C backend ci
	$(MAKE) -C frontend ci

.PHONY: docs
docs:
	$(MAKE) -C backend docs
