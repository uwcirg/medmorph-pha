#!/bin/sh
# fail on first error
set -e

cmdname="$(basename "$0")"
script_path="$(cd "$(dirname "$0")" && pwd)"
repo_path="$(readlink -f "${script_path}/..")"


usage() {
   cat << USAGE >&2
Usage:
   $cmdname [-h] [--help] fhir-server-url
   -h
   --help
          Show this help message

   fhir-server-url
          FHIR server base URL

    Remove PHI
USAGE
   exit 1
}



if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# 
# LNAME = “Study ID" 
# FNAME = 016-002xxx 
# 
# replace Patient Id
# 
# Patient ID = “**redacted**” 
# 
# Or “0” 
# Or use digits from FNAME 
FNAME=MEREDITH
sed -i "s|$FNAME|016-002001|g" "${repo_path}/test-data/Bundle_cancer-report.json"

LNAME=SHEPHERD
sed -i "s|$LNAME|Study ID|g" "${repo_path}/test-data/Bundle_cancer-report.json"

PTID=12746018
sed -i "s|$PTID|0|g" "${repo_path}/test-data/Bundle_cancer-report.json"

