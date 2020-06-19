#!/usr/bin/env bash
# #############################################################################
# Helper script to check zip code using an online tool from usps.com
# Usage: check-zip-with-usps.sh <zip code>
# #############################################################################
debug() { if [ "${DEBUG}" == "true" ]; then >&2 echo $@; fi; }

check_zip() {
    debug "Checking ${1} zip..."
    resp=$(curl -sL 'https://tools.usps.com/tools/app/ziplookup/cityByZip' \
            -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36' \
            -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' \
            --data "zip=${1}")
    echo "${resp}" | grep "SUCCESS" >/dev/null
    if [ $? -eq 0 ]; then echo "${1}-SUCCESS;${resp}";
    else echo "${1}-INVALID"; return 1; fi
}


check_zip "${1}" || exit 1
