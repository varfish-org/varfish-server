# syntax=docker/dockerfile:1.3

# ---------------------------------------------------------------------------
# NodeJS Base Image
# ---------------------------------------------------------------------------

FROM node:16-slim AS node-base

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

WORKDIR /usr/src/app

# ---------------------------------------------------------------------------
# NodeJS Dependencies
# ---------------------------------------------------------------------------

FROM node-base AS node-deps

COPY varfish/vueapp/package.json varfish/vueapp/package-lock.json \
     varfish/vueapp/

RUN npm ci --prefix varfish/vueapp

# ---------------------------------------------------------------------------
# NodeJS Build
# ---------------------------------------------------------------------------

FROM node-deps AS node-build

COPY cases/vueapp ./cases/vueapp
COPY clinvar_export/vueapp ./clinvar_export/vueapp
COPY cohorts/vueapp ./cohorts/vueapp
COPY svs/vueapp ./svs/vueapp
COPY varfish/vueapp ./varfish/vueapp
COPY variants/vueapp ./variants/vueapp

RUN npm run build --prefix varfish/vueapp

# ---------------------------------------------------------------------------
# Python Base Image
# ---------------------------------------------------------------------------

FROM python:3.10-bullseye AS python-base

MAINTAINER Manuel Holtgrewe <manuel.holtgrewe@bih-charite.de>
LABEL org.opencontainers.image.source https://github.com/bihealth/varfish-server

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static

WORKDIR /usr/src/app

RUN apt-get update && \
        apt-get install -y curl ldap-utils libldap2-dev libsasl2-dev
RUN apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/


# ---------------------------------------------------------------------------
# Python Dependencies
# ---------------------------------------------------------------------------

FROM python-base AS python-deps

# Install conda environment with varfish-server-worker.
RUN ["/bin/bash","-c", "cd /tmp && \
        wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh && \
        bash Mambaforge-Linux-x86_64.sh -b -p /opt/miniconda3 && \
        source /opt/miniconda3/bin/activate && \
        conda install -c conda-forge -y mamba && \
        mamba create -c conda-forge -c bioconda -y \
            -n varfish-server \
            varfish-server-worker==0.8.0 && \
        rm -f Mambaforge-Linux-x86_64.sh"]

# Add postgres 12 repository
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y \
        apt-utils \
        gcc \
        make \
        postgresql-client-12 \
        wget \
        xmlsec1 \
        gnupg2

# Install pip and pipenv
RUN python -m pip install -U pip pipenv

# Copy Pipfile and lock into the Docker image.
COPY Pipfile Pipfile.lock .

# Install Python dependencies via pipenv.
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install \
        --python=/usr/local/bin/python \
        --categories=packages,prod-packages,ldap-packages \
        --deploy && \
    pipenv run python -m nltk.downloader stopwords


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
COPY . .

# Build sphinx manual.
RUN pipenv run make -C docs_manual clean html


# ---------------------------------------------------------------------------
# Python Runtime
# ---------------------------------------------------------------------------

FROM python-base as python-runtime

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
COPY --from=python-docs /usr/src/app/docs_manual/_build/html ./docs_manual/_build/html

# Copy in the built NodeJS files
COPY --from=node-build /usr/src/app/varfish/vueapp/static ./varfish/vueapp/static

# Copy in the source code, includes VERSION file.
COPY . .

# Get icons
RUN python manage.py geticons -c \
        mdi bi cil fa-regular fa-solid fluent gridicons octicon icon-park-outline

# Prepare static files, including build NodeJS files.
RUN python manage.py collectstatic --no-input

# Clear the environment variables again.
RUN unset DJANGO_SECRET_KEY; \
    unset DJANGO_SETTINGS_MODULE; \
    unset DATABASE_URL

# Define the entry point
COPY --chmod=u+x utils/docker/docker-entrypoint.sh /usr/local/bin
ENTRYPOINT ["/usr/local/bindocker-entrypoint.sh"]
CMD ["wsgi"]
EXPOSE 8080/tcp