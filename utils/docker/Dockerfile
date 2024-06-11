# syntax=docker/dockerfile:1.3

# ---------------------------------------------------------------------------
# NodeJS Base Image
# ---------------------------------------------------------------------------

FROM node:20-slim AS node-base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

WORKDIR /usr/src/app


# ---------------------------------------------------------------------------
# NodeJS Dependencies
# ---------------------------------------------------------------------------

FROM node-base AS node-deps

COPY frontend/package.json frontend/package-lock.json \
     frontend/

RUN npm ci --prefix frontend/


# ---------------------------------------------------------------------------
# NodeJS Build
# ---------------------------------------------------------------------------

FROM node-deps AS node-build

COPY frontend/ frontend/

RUN npm run build --prefix frontend/


# ---------------------------------------------------------------------------
# Python Base Image
# ---------------------------------------------------------------------------

FROM python:3.10-bookworm AS python-base

LABEL org.opencontainers.image.authors="Manuel.Holtgrewe@bih-charite.de"
LABEL org.opencontainers.image.source https://github.com/varfish-org/varfish-server

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static

WORKDIR /usr/src/app

# Add postgres 12 repository
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && \
    apt-get install -y curl ldap-utils libldap2-dev libsasl2-dev \
        postgresql-client-12
RUN apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/


# ---------------------------------------------------------------------------
# Python Dependencies
# ---------------------------------------------------------------------------

FROM python-base AS python-deps

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y \
        apt-utils \
        gcc \
        make \
        wget \
        xmlsec1 \
        gnupg2

# Install pip and pipenv
RUN python -m pip install -U pip pipenv

# Copy Pipfile and lock into the Docker image.
COPY backend/Pipfile backend/Pipfile.lock ./

# Install Python dependencies via pipenv.
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install \
        --python=/usr/local/bin/python \
        --categories=packages,prod-packages,ldap-packages \
        --deploy


# ---------------------------------------------------------------------------
# Python Docs Dependencies
# ---------------------------------------------------------------------------

FROM python-deps AS python-docs-deps

# Install "dev-packages" as well.
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install \
        --python=/usr/local/bin/python \
        --categories=packages,dev-packages,ldap-packages \
        --deploy

# ---------------------------------------------------------------------------
# Python Docs
# ---------------------------------------------------------------------------

FROM python-docs-deps AS python-docs

# Copy source code for building the manual.
COPY VERSION backend/
COPY backend/ backend/
COPY docs/ docs/

# Build sphinx manual.
RUN pipenv run make -C docs clean html


# ---------------------------------------------------------------------------
# Python Runtime
# ---------------------------------------------------------------------------

FROM python-base as python-runtime

# Install runtime dependencies
RUN apt-get install -y libsqlite3-dev

# Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Copy the worker from the dedicated worker build.
COPY --from=ghcr.io/varfish-org/varfish-server-worker:main /usr/local/bin/varfish-server-worker /usr/local/bin/varfish-server-worker

# Copy virtual env from python-deps stage
COPY --from=python-deps /usr/src/app/.venv /usr/src/app/.venv
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# Temporarily setup environment variables for ``manage.py` commands below.
# We will clear them again later.
ENV DJANGO_SECRET_KEY=for-build-only \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    DATABASE_URL=postgres://sodar:sodar@fake/sodar

# Download files from CDN.
RUN mkdir -p local-static/local/css && \
    mkdir -p local-static/local/fonts && \
    mkdir -p local-static/local/js && \
    wget -P local-static/local/fonts \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/FontAwesome.otf \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.eot \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.svg \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff2 && \
    \
    wget -P local-static/local/css \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css \
        https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css \
        https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.18/css/bootstrap-select.min.css \
        https://cdn.datatables.net/1.10.24/css/dataTables.jqueryui.min.css \
        https://cdn.jsdelivr.net/npm/bootstrap4-tagsinput@4.1.3/tagsinput.css && \
    \
    wget -P local-static/local/js \
        https://code.jquery.com/jquery-3.5.1.min.js \
        https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.4/js/tether.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/shepherd/1.8.1/js/shepherd.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.0/clipboard.min.js \
        https://browser.sentry-cdn.com/6.2.5/bundle.tracing.min.js \
        https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.18/js/bootstrap-select.min.js \
        https://cdn.jsdelivr.net/npm/bootstrap4-tagsinput@4.1.3/tagsinput.js \
        https://cdnjs.cloudflare.com/ajax/libs/jsrender/1.0.11/jsrender.min.js \
        https://cdn.plot.ly/plotly-1.54.5.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/axios/0.21.1/axios.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/google-palette/1.1.0/palette.min.js \
        https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js

# Copy in the built manual.
COPY --from=python-docs /usr/src/app/docs/_build/html ./docs/_build/html

# Copy in the built NodeJS files
COPY --from=node-build /usr/src/app/frontend/static ./frontend/static

# Copy in the source code, includes VERSION file.
COPY VERSION VERSION
COPY backend/ .

# Get icons
RUN python manage.py geticons -c \
        mdi bi cil fa-regular fa-solid fluent gridicons octicon icon-park-outline

# Prepare static files, including build NodeJS files.
RUN CUSTOM_STATIC_DIR=frontend/static \
    python manage.py collectstatic --no-input

# Clear the environment variables again.
RUN unset DJANGO_SECRET_KEY; \
    unset DJANGO_SETTINGS_MODULE; \
    unset DATABASE_URL

# Define the entry point
COPY utils/docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["wsgi"]
EXPOSE 8080/tcp
