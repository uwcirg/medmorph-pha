#!/bin/sh
# fail on first error
set -e

cmdname="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="$(readlink -f "${script_path}/..")"

# add scripts/ directory to PATH
PATH=${PATH}:${script_path}

usage() {
   cat << USAGE >&2
Usage:
   $cmdname [-h] [--help]
   -h
   --help
          Show this help message

    Reset HIMSS demo to default state, using DB dump at hardcoded path (managed by symlink)
USAGE
   exit 1
}



if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

DB_DUMP="${repo_path}/test-data/reset-snapshot.sql"

echo Resetting...
restore-database.sh "$DB_DUMP"
