SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black
black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src)/' $(arg) .

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
	celery worker -A config.celery_app -l info --concurrency=4 --beat

.PHONY: collectstatic
collectstatic:
	python manage.py collectstatic

# Remember to execute 'python manage.py collectstatic' before executing tests the first time
.PHONY: test
test: collectstatic
	VARFISH_KIOSK_MODE=0 coverage run manage.py test -v2 --settings=config.settings.test
	coverage report

.PHONY: test-noselenium
test-noselenium:
	VARFISH_KIOSK_MODE=0 SKIP_SELENIUM=1 coverage run manage.py test -v2 --settings=config.settings.test
