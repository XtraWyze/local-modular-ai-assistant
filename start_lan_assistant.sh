#!/bin/sh
cd "$(dirname "$0")"
exec python3 lan_launcher.py "$@"
