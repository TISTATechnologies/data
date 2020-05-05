#!/usr/bin/env bash
# #############################################################################
## Deploy all files from the specific directory to the AWS S3 Bucket
## Usage: {SCRIPT_NAME} <source path> <bucket> [target directory]
##
## System environment:
##   CACHE_MAX_AGE=seconds  - HTTP Cache-Control max-age value, default: 86400 (24 hours)
##   FORCE=true             - remove all data in the target directory first, default: false
#
# #############################################################################
debug() { if [ "${DEBUG}" == "true" ]; then >&2 echo $@; fi; }
error() { echo "${1:-"Error"}"; exit 1; }

src=${1:-"--help"}
bucket=${2}
target=${3}
exclude='.*'
cache_max_age=${CACHE_MAX_AGE:-"86400"}
s3_target_url="s3://$(echo "${bucket}/${target}" | sed 's/\/\//\//g' | sed 's/\/$//g')"

if [ "${src}" == "--help" ] || [ -z "${bucket}" ]; then
    sed -n '/^##/,/^$/s/^## \{0,1\}//p' "$0" | sed 's/{SCRIPT_NAME}/'"$(basename "${0}")"'/g'
    exit 1
fi

echo "Upload data from ${src} to the ${s3_target_url}"
read -p "Continue (y/N)? " opt
if [ "${opt}" != "y" ] && [ "${opt}" != "Y" ]; then error "Skip"; fi

if [ "${FORCE}" == "true" ]; then
    read -p "All data in ${s3_target_url} will be deleted. Continue (y/N)?" opt
    if [ "${opt}" != "y" ] && [ "${opt}" != "Y" ]; then error "Skip"; fi
    aws s3 rm --recursive "${s3_target_url}"
fi

if [ -f "${src}" ]; then
    echo "Uploading file ${src}..."
    aws s3 cp "${src}" "${s3_target_url}/" --cache-control max-age=${cache_max_age} || error
else
    echo "Uploading files from ${src} directory..."
    aws s3 sync --exclude "${exclude}" "${src}" "${s3_target_url}" --cache-control max-age=${cache_max_age} || error
    echo "Creating _list.txt file..."
    tmpfile=/tmp/_list.txt
    echo "size       file" > "${tmpfile}"
    aws s3 ls --recursive "${s3_target_url}" | awk '{printf "% 10s %s\n",$3, $4}' >> "${tmpfile}"  || error
    aws s3 cp "${tmpfile}" "${s3_target_url}/" --cache-control max-age=${cache_max_age} || error
    echo "Complete create _list.txt file."
fi
if [ $? -ne 0 ]; then error; fi
echo "Success"
