#!/bin/sh
# fail on first error
set -e

cmdname="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="$(readlink -f "${script_path}/..")"

# default Bundle acted on, if filename not given
default_file="${repo_path}/test-data/Bundle_cancer-report_connectathon-2022-01.json"

usage() {
   cat << USAGE >&2
Usage:
   $cmdname [-h] [--help] [file-with-phi]
   -h
   --help
          Show this help message

   file-with-phi
          File with PHI to remove

    Remove PHI from given file, or default of $default_file
USAGE
   exit 1
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# Use given filename, or default if none given
phi_file=${1:-$default_file}

# HIMSS22 demo Patient details
FNAME=Akari
LNAME=Nakamura
PTID=12746018

# replace first name with a fixed Study ID
sed -i "s|$FNAME|016-002001|g" "$phi_file"

# replace last name with phrase "Study ID"
sed -i "s|$LNAME|Study ID|g" "$phi_file"

# replace patient ID with "0"
# NB replacing patient ID with the phrase "**redacted**" causes errors
sed -i "s|$PTID|10|g" "$phi_file"

echo File scrubbed of visible PHI:
echo $phi_file
