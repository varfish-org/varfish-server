#!/bin/bash

BUILD_NO=0

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

GIT_DESCRIBE=$(git describe | cut -d - -f 1)
GIT_TAG=${GIT_TAG-$GIT_DESCRIBE}
DOCKER_VERSION=$(echo $GIT_TAG | sed -e 's/^v//')-$BUILD_NO

docker build . \
    --build-arg app_git_tag=$GIT_TAG \
    -t bihealth/varfish-server:$DOCKER_VERSION
