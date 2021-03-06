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

    POST cancer Bundle report to given FHIR server's \$process-message endpoint
USAGE
   exit 1
}



if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi


FHIR_BASE_URL="$1"

cancer_bundle_path="${repo_path}/test-data/Bundle_cancer-report_connectathon-2022-01.json"

curl \
    --header "Content-Type: application/json" \
    --data @${cancer_bundle_path} \
    ${FHIR_BASE_URL}'/$process-message'
