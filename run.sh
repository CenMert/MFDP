#!/usr/bin/env bash
# Works from any directory (e.g. a .desktop launcher): the app uses cwd-relative paths.
cd "$(dirname "$(readlink -f "$0")")" || exit 1
source .venv/bin/activate
exec python -m mfdp_app.main
