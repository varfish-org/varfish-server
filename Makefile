SHELL = /bin/bash
MANAGE = time python manage.py

.PHONY: black collectstatic serve serve_public flushdb migrate shell celery test test-noselenium

black:
	black -l 100 --exclude '/(\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.?v?env|_build|buck-out|build|dist|src)/' .

serve:
	$(MANAGE) runserver

serve_public:
	$(MANAGE) runserver 0.0.0.0:8000

flushdb:
	$(MANAGE) flush

_migrate:
	$(MANAGE) makemigrations
	$(MANAGE) migrate

migrate: _migrate black

shell:
	$(MANAGE) shell

docs:
	$(MAKE) -C docs_manual html

celery:
	celery worker -A config.celery_app -l info --concurrency=4 --beat

collectstatic:
	python manage.py collectstatic

# Remember to execute 'python manage.py collectstatic' before executing tests the first time
test: collectstatic
	VARFISH_KIOSK_MODE=0 coverage run manage.py test -v2 --settings=config.settings.test
	coverage report

test-noselenium:
	VARFISH_KIOSK_MODE=0 SKIP_SELENIUM=1 coverage run manage.py test -v2 --settings=config.settings.test
