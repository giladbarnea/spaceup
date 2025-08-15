#!/usr/bin/env bash

if [[ -t 1 && -t 0 ]]; then
    uv run python -m pytest tests --color=yes --code-highlight=yes "$@"
else
    uv run python -m pytest tests --color=no --code-highlight=no "$@"
fi
