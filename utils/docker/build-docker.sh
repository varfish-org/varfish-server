#!/bin/bash

# Utility script to start the Docker build process.

set -x
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Write /VERSION file for server to know its version.
git describe --tags >$DIR/VERSION

# Obtain version for the Docker image.
IMAGE_TAG=${IMAGE_TAG:-adhoc}

# Explicitely set organization and repository name for Docker image.
ORG=bihealth
REPO=varfish-server

# Set value for WORKER_GIT_TREEISH.
WORKER_GIT_TREEISH=${WORKER_GIT_TREEISH:-main}

# Actually start the Docker build.
docker build . \
    --build-arg WORKER_GIT_TREEISH=${WORKER_GIT_TREEISH} \
    --file $DIR/Dockerfile \
    -t ghcr.io/$ORG/$REPO:$IMAGE_TAG \
    "$@"
