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
	format-black \
	format-protolint

.PHONY: format-isort
format-isort:
	pipenv run isort --force-sort-within-sections --profile=black .

.PHONY: format-black
format-black:
	pipenv run black --line-length 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' .

.PHONY: format-protolint
format-protolint:
	protolint -fix .

.PHONY: lint
lint: \
	lint-isort \
	lint-black \
	lint-flake8 \
	lint-protolint
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

.PHONY: lint-protolint
lint-protolint:
	protolint .

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
		--file ./varfish/tests/drf_openapi_schema/varfish_api_schema.yaml

# Download the .proto files and modify them.
.PHONY: protos-download
protos-download:
	mkdir -p protos/seqvars/protos
	rm -f protos/seqvars/protos/*_p*2*.py

	wget -O protos/seqvars/protos/output.proto \
		https://raw.githubusercontent.com/varfish-org/varfish-server-worker/main/protos/varfish/v1/seqvars/output.proto
	wget -O protos/seqvars/protos/query.proto \
		https://raw.githubusercontent.com/varfish-org/varfish-server-worker/main/protos/varfish/v1/seqvars/query.proto

	mkdir -p seqvars/protos
	touch seqvars/protos/__init__.py

	sed -i \
		-e 's|package varfish.v1.seqvars|package seqvars.pbs|' \
		-e 's|package varfish.v1.seqvars;|package seqvars.pbs|' \
		-e 's|varfish\.v1\.seqvars\.query|seqvars.pbs.query|' \
		-e 's|varfish/v1/seqvars|seqvars/protos|' \
		protos/seqvars/protos/*.proto

	PYTHONPATH=. \
		protoc \
		-Iprotos \
		--python_out=. \
		--mypy_out=. \
		protos/seqvars/protos/*.proto

# Build the protobuf Python files, then format.
.PHONY: protos
protos: protos-download format lint
