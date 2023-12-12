#!/usr/bin/env bash

script_path=$(readlink -f "$0")
dir=$(dirname "$script_path")

"$dir/venv/bin/python3" "$dir/recode_video.py" "$@"
