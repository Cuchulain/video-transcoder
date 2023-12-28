#!/usr/bin/env bash

script_path=$(readlink -f "$0")
dir=$(dirname "$script_path")

interpret="$dir/venv/bin/python3"
if [ ! -f "$interpret" ]; then
  interpret="python3"
fi

"$interpret" "$dir/recode_video.py" "$@"
