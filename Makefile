SHELL = /bin/bash
MANAGE = time python manage.py

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
migrate: _migrate black isort

.PHONY: shell
shell:
	$(MANAGE) shell

.PHONY: docs
docs:
	$(MAKE) -C docs_manual html

.PHONY: celery
celery:
	pipenv run watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- \
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
	npm run --prefix varfish/vueapp type-check $(arg)
	npm run --prefix varfish/vueapp prettier-check $(arg)

.PHONY: prettier
prettier:
	npm run --prefix varfish/vueapp prettier-write $(arg)

coverage:
	coverage report
	coverage html


.PHONY: lint
lint: lint-flake8 lint-isort

.PHONY: lint-flake8
lint-flake8:
	flake8

.PHONY: lint-isort
lint-isort:
	isort --force-sort-within-sections --profile=black --check .

.PHONY: lint-black
lint-black:
	black --line-length 100 --check --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' .

.PHONY: format
format: format-isort format-black

.PHONY: format-isort
format-isort:
	isort --force-sort-within-sections --profile=black .

.PHONY: format-black
format-black:
	black --line-length 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src|node_modules)/' .
