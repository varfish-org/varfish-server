#!/bin/bash

# Utility script to start the Docker build process.

set -x
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Write /VERSION file for server to know its version.
git describe --tags >$DIR/../../VERSION

# Obtain version for the Docker image.
IMAGE_TAG=${IMAGE_TAG:-adhoc}

# Explicitely set organization and repository name for Docker image.
ORG=varfish-org
REPO=varfish-server

# Write out VERSION file for Docker
git describe --tags > VERSION

# Actually start the Docker build.
docker build . \
    $(if [[ ${SINGLE_THREAD-0} -eq 1 ]]; then echo --config $DIR/buildkitd.toml; fi) \
    --file $DIR/Dockerfile \
    -t ghcr.io/$ORG/$REPO:$IMAGE_TAG \
    "$@"
