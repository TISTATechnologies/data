#!/usr/bin/env bash
show_help() {
    echo "Calculate/build dat for a custom us area."
    echo "Usage: $(basename "${0}") <area fips>"
    exit 1
}

AREA_FIPS=${1:-"--help"}
if [ "${AREA_FIPS}" == "--help" ]; then show_help; fi
cd "$(dirname "${0}")"
echo "Working directory ${PWD}"

area_file=../../../common/us/areas.json
counties_file=../../../common/us/counties.csv
population_file=../../../common/us/population.csv
zips_file=../../../common/us/zips.csv
echo "Processing ${AREA_FIPS} custom us area (file: ${area_file})..."
full_info=$(jq -r '.[] | select(.fips == "'${AREA_FIPS}'")' "${area_file}")
if [ -z "${full_info}" ]; then echo "Error: area '${AREA_FIPS}' not found."; exit 1; fi

#------ add area to the counties.csv --------------------------------
mv "${counties_file}" "${counties_file}.orig"
name=$(echo "${full_info}" | jq -r '.name')
lat=$(echo "${full_info}" | jq -r '.latitude')
lon=$(echo "${full_info}" | jq -r '.longitude')
head -n 1 "${counties_file}.orig" > "${counties_file}"
(sed '1d;' "${counties_file}.orig"; echo "${AREA_FIPS},US,${name},${lat},${lon}") \
| sort -u >> "${counties_file}"
rm -f "${counties_file}.orig"

#------ Get all zips and calculate population fr the area -----------
population=0
zips=
all_fips=$(echo "${full_info}" | jq -r '.counties[].fips' )
for fips in ${all_fips}; do
    echo "[${fips}]..."
    population_tmp=$(grep ",${fips}," "${population_file}" | head -n 1 | awk -F"," '{printf "%d",$3}')
    echo "[${fips}] population = ${population_tmp}"
    population=$(( $population + $population_tmp ))
    zips_tmp=$(grep ",${fips}$" "${zips_file}" | grep -v ',US' | cut -d"," -f1 | xargs)
    echo "[${fips}] zips = ${zips_tmp}"
    zips="${zips_tmp} ${zips}"
done

#------ Update population.csv --------------------------------
if [ ${population} -gt 0 ]; then
    echo "Write population to the file: ${population_file}"
    echo "US,${AREA_FIPS},${population}"
    # add new area population record and reorder all file.
    # the 'complicated' logic need to order by two value: state-fips,county-fips
    # 1. cut header
    # 2. add first colum with id = "real fips for county, "reverted" fips for state"
    # 3. orer by first field and remove this field from the output
    mv "${population_file}" "${population_file}.orig"
    head -n 1 "${population_file}.orig" > "${population_file}"
    (sed '1d;' "${population_file}.orig"; echo "US,${AREA_FIPS},${population}") \
    | awk -F',' '{printf "#%s:%s|%s\n", $2, $2, $0}' | sed 's/#000/#/g' | sed 's/://g' \
    | sort -u \
    | cut -d"|" -f2  >> "${population_file}"
    rm -f "${population_file}.orig"
else
    echo "Error: population not found!"
fi

#------ add area to the zips.csv --------------------------------
if [ -n "${zips}" ]; then
    echo "Write zips+fips to the file: ${zips_file}"
    echo "${zips}"
    # add new zips and reorder all file
    mv "${zips_file}" "${zips_file}.orig"
    head -n 1 "${zips_file}.orig" > "${zips_file}"
    (sed '1d;' "${zips_file}.orig"; for zip in ${zips}; do echo "${zip},${AREA_FIPS}"; done) \
    | sort -u >> "${zips_file}"
    rm -f "${zips_file}.orig"
else
    echo "Error: zips not found!"
fi
echo "Done"