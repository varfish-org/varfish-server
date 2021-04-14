#!/bin/bash

BUILD_NO=0

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR

GIT_DESCRIBE=$(git describe --tags | cut -d - -f 1)
GIT_TAG=${GIT_TAG-$GIT_DESCRIBE}
DOCKER_VERSION=$(echo $GIT_TAG | sed -e 's/^v//')-$BUILD_NO
GIT_DEPTH=$(($(git rev-list HEAD ^$(git describe --abbrev=0 --tags) --count) + 1))
GIT_URL=https://github.com/bihealth/varfish-server.git

docker build . \
    --build-arg app_git_tag=$GIT_TAG \
    --build-arg app_git_depth=$GIT_DEPTH \
    --build-arg app_git_url=$GIT_URL \
    -t bihealth/varfish-server:$DOCKER_VERSION
