#!/usr/bin/env bash
# #############################################################################
## Upload all data from the build/common directory to the s3 bucket
## Usage: upload-common-to-s3-bucket <s3 bucket name>
# #############################################################################
version=${VERSION:-"2"}
bucket=${1:-"${S3_BUCKET:-"data-dev.tistatech.com"}"}

cd $(dirname "${0}")/../..
src_dir=${PWD}/build/common/v${version}
target=/common/v${version}

if [ ! -d "${src_dir}" ]; then echo "Directory ${src_dir} not found."; exit 1; fi

echo "Upload all files into the s3 bucket"
echo "Source: ${src_dir}"
echo "Target: s3://$(echo "${bucket}/${target}" | sed 's/\/\//\//g')"
export CACHE_MAX_AGE=1800
./scripts/upload-to-s3-bucket.sh "${src_dir}" "${bucket}" "${target}" \
&& echo "Complete upload all files from ${src_dir}."
