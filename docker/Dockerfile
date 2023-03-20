# syntax=docker/dockerfile:1.3

# ---------------------------------------------------------------------------
# Build varfish-server-worker
# ---------------------------------------------------------------------------
FROM rust:1-buster AS build-worker
ARG worker_git_url=https://github.com/bihealth/varfish-worker.git
ARG worker_git_treeish=v0.5.1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static

RUN git clone --depth 1 --branch $worker_git_treeish $worker_git_url /tmp/varfish-server-worker
RUN cd /tmp/varfish-server-worker && \
    cargo install --path .


# ---------------------------------------------------------------------------
# Build varfish-server (without worker)
# ---------------------------------------------------------------------------
FROM python:3.10-buster AS build-server

MAINTAINER Manuel Holtgrewe <manuel.holtgrewe@bih-charite.de>
LABEL org.opencontainers.image.source https://github.com/bihealth/varfish-server

ARG server_git_url=https://github.com/bihealth/varfish-server.git
ARG server_git_treeish
ARG server_git_depth=1

ENV DEBIAN_FRONTEND noninteractive
ENV CUSTOM_STATIC_DIR /usr/src/app/local-static

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Copy source code into Docker image.
RUN mkdir -p /usr/src
RUN git clone --depth $server_git_depth --branch $server_git_treeish $server_git_url /usr/src/app

# Add postgres 12 repository
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y \
        apt-utils \
        gcc \
        ldap-utils \
        libldap2-dev \
        libsasl2-dev \
        make \
        postgresql-client-12 \
        wget \
        xmlsec1 \
        gnupg2

# Install Python dependencies.
RUN cd /usr/src/app && \
    pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir -r requirements/local.txt && \
    python -m nltk.downloader stopwords

# Build sphinx manual.
RUN cd /usr/src/app/docs_manual && \
    make clean html

# Install miniconda3 and setup environment for annotation, required for Kiosk.
RUN ["/bin/bash","-c", "cd /tmp && \
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
        bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/miniconda3 && \
        source /opt/miniconda3/bin/activate && \
        conda install -c conda-forge -y mamba && \
        mamba create -c conda-forge -c bioconda -y -n varfish-annotator \
            varfish-annotator-cli=0.10=0 \
            htslib=1.9 \
            openjdk=8 \
            bcftools=1.9 && \
        rm -f Miniconda3-latest-Linux-x86_64.sh"]

# Install modern nodejs
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - && \
    apt install nodejs

# Install npm dependencies.
RUN cd /usr/src/app/varfish/vueapp && \
    npm ci && \
    npm run build

# Download files from CDN.
RUN mkdir -p /usr/src/app/local-static/local/css && \
    mkdir -p /usr/src/app/local-static/local/fonts && \
    mkdir -p /usr/src/app/local-static/local/js && \
    cd /usr/src/app/local-static/local/fonts && \
    wget \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/FontAwesome.otf \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.eot \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.svg \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.ttf \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/fonts/fontawesome-webfont.woff2 && \
    \
    cd /usr/src/app/local-static/local/css && \
    wget \
        https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css \
        https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css \
        https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.18/css/bootstrap-select.min.css \
        https://cdn.datatables.net/1.10.24/css/dataTables.jqueryui.min.css \
        https://cdn.jsdelivr.net/npm/bootstrap4-tagsinput@4.1.3/tagsinput.css && \
    \
    cd /usr/src/app/local-static/local/js && \
    wget \
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

# Get icons
RUN cd /usr/src/app && \
    DJANGO_SECRET_KEY=for-build-only \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    DATABASE_URL=postgres://sodar:sodar@fake/sodar \
    python manage.py geticons -c mdi bi cil fa-regular fa-solid fluent gridicons octicon icon-park-outline

# Prepare static files
RUN mkdir -p /usr/src/app/clinvar_export/vueapp/dist && \
    cd /usr/src/app && \
    npm --prefix varfish/vueapp run build && \
    DJANGO_SECRET_KEY=for-build-only \
      DJANGO_SETTINGS_MODULE=config.settings.production \
      DATABASE_URL=postgres://varfish:varfish@fake/varfish \
      python manage.py collectstatic --no-input

# Define the entry point.
COPY docker-entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && \
    ln -s /usr/local/bin/docker-entrypoint.sh / # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["wsgi"]
EXPOSE 8080/tcp


# ---------------------------------------------------------------------------
# Combine varfish-server and -worker
# ---------------------------------------------------------------------------
FROM build-server AS combined
COPY --from=build-worker /root/.cargo/bin/varfish-server-worker /usr/local/bin/varfish-server-worker
RUN /usr/local/bin/varfish-server-worker --help
