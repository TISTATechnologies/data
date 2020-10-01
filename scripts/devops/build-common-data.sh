#!/usr/bin/env bash
# #############################################################################
## Preparing public data files before deploying it to the static site.
## Required:
## * csvtojson  - use 'npm install csvtojson' to install this tool
# #############################################################################
title() { echo "************************************************************"; echo "* $@"; }

version=${VERSION:-"2"}

cd $(dirname "${0}")/../..
data_dir=${PWD}
output_dir=${PWD}/build/common/v${version}

title "Building '${output_dir}' directory..."
rm -rf "${output_dir}"
mkdir -p "${output_dir}" 2>/dev/null
cp -vaT "${data_dir}/common" "${output_dir}" || exit 1
title "Creating files with US zips..."
./scripts/converter/create-us-zips-cache-directory.py "${output_dir}/us/zip" || exit 1
title "Creating json format for all csv files..."
MINIFY=true ./scripts/converter/csv-to-json.sh "${output_dir}" || exit 1
title "Build 'common' directory complete: ${output_dir}"
