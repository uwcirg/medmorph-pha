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


# Connectathon Patient details
cancer_bundle_path="${repo_path}/test-data/Bundle_cancer-report_connectathon-2022-01.json"
FNAME=MEREDITH
LNAME=SHEPHERD
PTID=12746018

# replace first name with a fixed Study ID
sed -i "s|$FNAME|016-002001|g" "$cancer_bundle_path"

# replace last name with phrase "Study ID"
sed -i "s|$LNAME|Study ID|g" "$cancer_bundle_path"

# replace patient ID with "0"
# NB replacing patient ID with the phrase "**redacted**" causes errors
sed -i "s|$PTID|0|g" "$cancer_bundle_path"

echo Bundle file scrubbed of visible PHI:
echo $cancer_bundle_path
