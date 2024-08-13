#!/bin/bash

git config --global --add safe.directory $GITHUB_WORKSPACE

tag=$(python -m action $INPUT_BUMP_STYLE | tr -d '[:space:]')
echo "TAG_NAME=$tag" >> $GITHUB_OUTPUT
echo "TAG: $tag"
