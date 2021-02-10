FROM python:3.6-buster

ARG app_git_url=https://github.com/bihealth/varfish-server.git
ARG app_git_tag

ENV DEBIAN_FRONTEND noninteractive

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /usr/local/bin/wait
RUN chmod +x /usr/local/bin/wait

# Copy source code into Docker image.
RUN mkdir -p /usr/src
RUN git clone --depth 1 --branch $app_git_tag $app_git_url /usr/src/app

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y \
        apt-utils
RUN apt-get install -y \
        gcc \
        ldap-utils \
        libldap2-dev \
        libsasl2-dev \
        make \
        postgresql-client

# Install Python dependencies.
RUN cd /usr/src/app && \
    pip install --no-cache-dir -r requirements/production.txt && \
    pip install --no-cache-dir -r requirements/local.txt

# Prepare static files
RUN cd /usr/src/app && \
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
