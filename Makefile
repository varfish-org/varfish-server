SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black
black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' $(arg) .

.PHONY: npm-install
npm-install:
	cd varfish/vueapp && npm ci

.PHONY: serve
serve:
	$(MANAGE) runserver

.PHONY: vue_serve
vue_serve:
	npm run --prefix varfish/vueapp serve

.PHONY: vue_build
vue_build:
	npm run --prefix varfish/vueapp build

.PHONY: storybook
storybook:
	npm run --prefix varfish/vueapp storybook

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

.PHONY: vue_test
vue_test:
	npm run --prefix varfish/vueapp test:unit $(arg)

.PHONY: vue_test-coverage
vue_test-coverage:
	npm run --prefix varfish/vueapp test:unit-coverage $(arg)

.PHONY: vue_lint
vue_lint:
	npm run --prefix varfish/vueapp lint $(arg)
	npm run --prefix varfish/vueapp prettier-check $(arg)

.PHONY: prettier
prettier:
	npm run --prefix varfish/vueapp prettier-write $(arg)

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
