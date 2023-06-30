#!/bin/bash

# Utility script to start the Docker build process.

set -x
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

# Write /VERSION file for server to know its version.
git describe --tags >VERSION

# Obtain version for the Docker image.
DOCKER_VERSION=$(git describe --tags | cut -d - -f 1 sed -e 's/^v//')

# Explicitely set organization and repository name for Docker image.
ORG=bihealth
REPO=varfish-server

# Actually start the Docker build.
docker build . \
    --file utils/docker/Dockerfile \
    --pull \
    -t ghcr.io/$ORG/$REPO:$DOCKER_VERSION \
    "$@"
