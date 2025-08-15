#!/usr/bin/env bash

env | grep -e CURSOR -e CODE
if [[ -t 1 && -t 0 && "$USER" = giladbarnea && "$LOGNAME" = giladbarnea ]]; then
    uv run python -m pytest tests --color=yes --code-highlight=yes "$@"
else
    uv run python -m pytest tests --color=no --code-highlight=no -vv "$@"
fi
