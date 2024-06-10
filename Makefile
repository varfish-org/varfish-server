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
	make -C backend deps
	make -C frontend deps

.PHONY: format
format:
	make -C backend format
	make -C frontend format

.PHONY: lint
lint:
	make -C backend lint
	make -C frontend lint

.PHONY: test
test:
	make -C backend test
	make -C frontend test

.PHONY: ci
ci:
	make -C backend ci
	make -C frontend ci

.PHONY: docs
docs:
	make -C backend docs
