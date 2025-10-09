#!/usr/bin/env bash
if [[ -t 1 && -t 0 && "$USER" = giladbarnea && "$LOGNAME" = giladbarnea && "$__CFBundleIdentifier" != com.jetbrains.pycharm && 
  -z "$CURSOR_AGENT" &&
  "$TERM_PROGRAM" != vscode &&
  "$VSCODE_INJECTION" != 1 &&
  -z "$CURSOR_TRACE_ID" ]] 
  ; then
  uv run python -m pytest tests --color=yes --code-highlight=yes "$@"
else
  uv run python -m pytest tests --color=no --code-highlight=no -vv "$@"
fi
