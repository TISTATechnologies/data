#!/usr/bin/env bash
# #############################################################################
## Prepeare result directory with all data files
# #############################################################################
version=${VERSION:-"1"}
title() { echo "************************************************************"; echo "* $@"; }
cd $(dirname "${0}")/../..
data_dir=${PWD}
output_dir=${PWD}/build/common/v${version}

title "Building '${output_dir}' directory..."
rm -rf "${output_dir}"
mkdir -p "${output_dir}" 2>/dev/null
cp -vaT "${data_dir}/common" "${output_dir}"
title "US zips files"
#./scripts/converter/create-us-zips-cache-directory.py "${output_dir}/us/zip"
title "Create json format for all csv files"
#MINIFY=true ./scripts/converter/csv-to-json.sh "${output_dir}"
title "Build 'common' directory complete: ${output_dir}"

