#!/usr/bin/env bash
set -x

uv run ruff check . --fix --unsafe-fixes --preview
uv run ruff format . --preview
