#!/bin/bash

function cleanup() {
    docker image prune --filter dangling=true -f
}

trap cleanup EXIT

docker compose up --watch