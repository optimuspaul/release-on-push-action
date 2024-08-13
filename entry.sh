#!/bin/bash

git config --global --add safe.directory $GITHUB_WORKSPACE
python -m action $INPUT_BUMP_STYLE
