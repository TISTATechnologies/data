#!/usr/bin/env bash
# #############################################################################
# Convert csv file into the json
# Usage: csv-to-json.sh <file|directory> [output directory]
#
# System environment:
#   MINIFY=true     - if you want to minify result JSON file
#
# Requirements:
#   jq, csvtojson
# #############################################################################
set -o pipefail
debug() { if [ "${DEBUG}" == "true" ]; then >&2 echo $@; fi; }

src=${1:-"--help"}
output=${2}
if [ "${src}" == "--help" ]; then
    echo "Usage: $(basename "${0}") file|directory> [output directory]"
    exit 1
fi

if [ -z "$(which csvtojson)" ]; then echo "Error: csvtojson tool is required"; exit 1; fi
if [ -z "$(which jq)" ]; then echo "Error: jq tool is required"; exit 1; fi

convert_file() {
    csv_file=${1}
    if [ -n "${2}" ]; then output_dir=$(echo "${2}/" | sed 's/\/\/$/\//g');
    else output_dir=; fi
    if [ "${MINIFY}" == "true" ]; then minify="-c"; else minify=; fi
    json_file="${output_dir}${csv_file%.*}.json"
    debug "Converting ${csv_file} -> ${json_file} (MINIFY=${MINIFY:-"false"})"
    mkdir -p "$(dirname "${json_file}")" 2>/dev/null
    # jq-1.5 has an error with pipeout without arguments. The '.' is necessary.
    csvtojson "${csv_file}" | jq . ${minify} > "${json_file}" || exit 1
    echo "Convert ${csv_file} -> ${json_file} complete" || exit 1
}


if [ -d "${src}" ];then
    # "readlink" for all platform: get absolute path
    src_full=$(python -c 'import os,sys;print(os.path.realpath(sys.argv[1]))' "${src}")
    output=${2:-"${src_full}"}

    echo "Converting all csv files to json inside the ${src_full} directory..."
    cd "${src_full}"
    find . -name "*.csv" | sort | while read f; do
        convert_file "${f}" "${output}"
    done
    echo "Convert csv to json complete."
else
    convert_file "${src}" "${output:-"$(dirname "${src}")"}"
fi
