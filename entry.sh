#!/bin/bash

git config --global --add safe.directory $GITHUB_WORKSPACE
echo "TAG_NAME=$(python -m action $INPUT_BUMP_STYLE)" >> "$GITHUB_OUTPUT"
