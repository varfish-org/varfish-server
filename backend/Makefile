# Set the shell to bash with printing of all commands (`-x`) and unofficial
# strict mode (`-euo pipefail`).
SHELL := bash -x -euo pipefail

# Shortcut to the management command.
MANAGE = time python manage.py

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
	@echo "  collectstatic Collect static files (Django)"
	@echo "  serve   Run the (development) server"
	@echo "  celery  Run celery"
	@echo "  migrate Create Django migrations and upgrade"
	@echo "  shell   Run Python shell"

.PHONY: deps
deps:
	pipenv install --dev --categories=packages,dev-packages

.PHONY: format
format:	\
	format-isort \
	format-black

.PHONY: format-isort
format-isort:
	pipenv run isort --force-sort-within-sections --profile=black .

.PHONY: format-black
format-black:
	pipenv run black --line-length 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' .

.PHONY: lint
lint: \
	lint-isort \
	lint-black \
	lint-flake8
	#lint-mypy

.PHONY: lint-isort
lint-isort:
	pipenv run isort --force-sort-within-sections --profile=black --check-only --diff .

.PHONY: lint-black
lint-black:
	pipenv run black --check --line-length 100 --diff --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' .

.PHONY: lint-flake8
flake8:
	pipenv run flake8 --max-line-length 100 .

# .PHONY: lint-mypy
# lint-mypy:
# 	MYPYPATH=$(PWD)/stubs pipenv run mypy $(DIRS_PYTHON_NO_ALEMBIC)

.PHONY: frontend-vite
frontend-vite:
	cd ../frontend && make deps build

.PHONY: geticons
geticons:
	pipenv run $(MANAGE) geticons -c mdi bi cil fa-regular fa-solid fluent gridicons octicon icon-park-outline

.PHONY: collectstatic
collectstatic: geticons frontend-vite
	pipenv run $(MANAGE) collectstatic --clear --no-input

.PHONY: test
test: collectstatic
	VARFISH_KIOSK_MODE=0 pipenv run coverage run manage.py test -v2 --settings=config.settings.test
	pipenv run coverage xml
	pipenv run coverage report

.PHONY: test-ci
test-ci: test

coverage:
	coverage report
	coverage html

.PHONY: ci
ci: \
	deps \
	lint \
	test-ci

.PHONY: docs
docs:
	pipenv run $(MAKE) -C ../docs clean html

.PHONY: _migrate
_migrate:
	pipenv run $(MANAGE) makemigrations
	pipenv run $(MANAGE) migrate

.PHONY: migrate
migrate: _migrate format

.PHONY: shell
shell:
	pipenv run $(MANAGE) shell

.PHONY: serve
serve:
	pipenv run $(MANAGE) runserver

.PHONY: serve-public
serve_public:
	pipenv run $(MANAGE) runserver 0.0.0.0:8000

.PHONY: celery
celery:
	pipenv run watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- \
		celery -A config.celery_app worker -l info --concurrency=4 --beat

.PHONY: gen-api-schema
gen-api-schema:
	pipenv run $(MANAGE) spectacular \
	| grep -v ^Loading \
	| grep -v '^The ' \
	> ./varfish/tests/drf_openapi_schema/varfish_api_schema.yaml
