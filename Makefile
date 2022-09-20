SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black
black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src)/' $(arg) .

.PHONY: npm-install
npm-install:
	cd varfish/vueapp && npm ci

.PHONY: serve
serve:
	$(MANAGE) runserver

.PHONY: serve_vue
serve_vue:
	npm run --prefix varfish/vueapp serve

.PHONY: serve_public
serve_public:
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: flushdb
flushdb:
	$(MANAGE) flush

.PHONY: _migrate
_migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

.PHONY: migrate
migrate: _migrate black

.PHONY: shell
shell:
	$(MANAGE) shell

.PHONY: docs
docs:
	$(MAKE) -C docs_manual html

.PHONY: celery
celery:
	celery -A config.celery_app worker -l info --concurrency=4 --beat

.PHONY: geticons
geticons:
	python manage.py geticons -c cil gridicons octicon icon-park-outline

.PHONY: collectstatic
collectstatic: geticons
	python manage.py collectstatic --clear --no-input

# Remember to execute 'python manage.py collectstatic' before executing tests the first time
.PHONY: test
test: collectstatic
	VARFISH_KIOSK_MODE=0 coverage run manage.py test -v2 --settings=config.settings.test
	coverage report

.PHONY: test-noselenium
test-noselenium:
	VARFISH_KIOSK_MODE=0 SKIP_SELENIUM=1 coverage run manage.py test -v2 --settings=config.settings.test

.PHONY: test_clinvar_export_vue
test_clinvar_export_vue:
	npm run --prefix varfish/vueapp test:unit $(arg)

.PHONY: lint_clinvar_export_vue
lint_clinvar_export_vue:
	npm run --prefix varfish/vueapp lint $(arg)

.PHONY: lint
lint: flake8

.PHONY: isort
isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: flake8
flake8:
	flake8

coverage:
	coverage report
	coverage html
