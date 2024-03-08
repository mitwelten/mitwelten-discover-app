#!/bin/bash

TAG=${1:-latest}

IMAGE_NAME="cr.gitlab.fhnw.ch/mitwelten/docker-infrastructure/mitwelten-discover_app:$TAG"

docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "Docker-Image '$IMAGE_NAME' built successfuly."
else
    echo "Error occured, could not build image with tag '$IMAGE_NAME'."
    exit 1
fi

docker push $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "Docker-Image '$IMAGE_NAME' was successfuly pushed to repository."
else
    echo "Error occured, could not push docker image '$IMAGE_NAME'"
fi
