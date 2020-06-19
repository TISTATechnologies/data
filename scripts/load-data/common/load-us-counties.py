#!/usr/bin/env python3
# #############################################################################
# Helper script to generate us-counties.csv file
# * Download counties information from census.gov
# * Download geo-location from datasciencetoolkit.org
# Save result into the '../../common/us/counties.csv' file
#
# requirements: pandas, xlrd
# #############################################################################
import codecs
import csv
import json
import os
import pandas
import re
import sys
from urllib import request, parse as urlparse
from pathlib import Path

codecs.register_error('strict', codecs.ignore_errors)
URL = 'https://www2.census.gov/programs-surveys/popest/geographies/2017/all-geocodes-v2017.xlsx'
# URL = f'file://{(Path(__file__).parent / "all-geocodes-v2017.xlsx").resolve()}'
CORRECT_US_STATES_COUNTIES_COUNT = 3143                        # value on end 2017
CORRECT_US_TERRITORIES_COUNTIES_COUNT = 78                     # value on 2020
output_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'counties.csv'
counties = []

# -----------------------------------------------------------------------------
# Show debug output only with the env.DEBUG = true
debug = lambda msg: print(msg) if os.environ.get('DEBUG') == 'true' else lambda msg: None


# -----------------------------------------------------------------------------
# Load all states {state_fips: (state_id, state_name)}
states_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'states.csv'
print(f'Read csv with states: {states_file}')
states = dict([(r[1].rjust(2, '0'), (r[0], r[2])) for r in csv.reader(states_file.open('r'), delimiter=',', quotechar='"')])


# -----------------------------------------------------------------------------
# Load geo location for a county
def get_geo_location(county_name, state_id):
    urlquery = urlparse.quote(f'address={county_name},{state_id},US')
    url = f'http://www.datasciencetoolkit.org/maps/api/geocode/json?{urlquery}'
    try:
        debug(f'Load geolocation from: {url}')
        response = codecs.decode(request.urlopen(url).read(), 'utf-8')
        debug(f'Parse data')
        data = json.loads(response)
        location = data['results'][0]['geometry']['location']
        debug(f'Found location: {location}')
        return (location['lat'], location['lng'])
    except Exception as ex:
        print(f'Error get/parse data from {url}')
        print(ex)
        raise ex


# -----------------------------------------------------------------------------
# Safety add county information to the main list
def add_county_to_the_list(fips, state_id, name, latitude=None, longitude=None):
    for item in counties:
        if item[0] == fips:
            debug(f'{fips}, {state_id}, {name} - Skip. Already exists in the list.')
            return
    if latitude is None or longitude is None:
        (latitude, longitude) = get_geo_location(name, state_id)
    print(f'{fips}, {state_id}, {name}, {latitude}, {longitude}')
    counties.append([fips, state_id, name, latitude, longitude])


# -----------------------------------------------------------------------------
# Main method
print(f'Load data from {URL}')
data = pandas.read_excel(URL, sheet_name=0)
print(f'Parsing data line by line')
name_replace_patterns = [
    re.compile(' city', re.IGNORECASE),
    re.compile(' town', re.IGNORECASE),
    re.compile(' county', re.IGNORECASE)
]

for row in data.itertuples():
    level = str(row._1)
    state_fips = str(row._2)
    county_fips = str(row._3)
    subdiv_fips = str(row._4)
    place_fips = str(row._5)
    city_fips = str(row._6)
    name = str(row._7)
    if not level.isdigit() or not state_fips.isdigit() or not county_fips.isdigit():
        debug(f'Skip header: {row}')
        continue            # Skip headers
    if county_fips == '000' or not (subdiv_fips == '00000' and place_fips == '00000' and city_fips == '00000'):
        debug(f'Skip non county: {row}')
        continue            # skip states and country and non county
    fips = f'{state_fips}{county_fips}'
    country_id = 'US'
    state_id = states[state_fips][0]
    if fips in ['02093', '02261']:
        # Skip: Valdez–Cordova Census Area (Alaska) - on Jan 2019
        debug(f'{fips}, {state_id}, {name} - Skip.')
    else:
        add_county_to_the_list(fips, state_id, name)

# Correction on 2020
# Jan 2019 update for Valdez–Cordova Census Area (Alaska)
add_county_to_the_list('02063', 'AK', 'Chugach Census Area', 61.130833, -146.348333)
add_county_to_the_list('02066', 'AK', 'Copper River Census Area', 62.109722, -145.557222)

# -----------------------------------------------------------------------------
# Write counties to the csv file
found_total_counties = len(counties)
with output_file.open('w') as file_writer:
    csv_writer = csv.writer(file_writer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['fips', 'state_id', 'name', 'latitude', 'longitude'])
    for county in sorted(counties, key=lambda x: x[0]):
        csv_writer.writerow(county)

# -----------------------------------------------------------------------------
# Show validation result
correct_counties_count = CORRECT_US_STATES_COUNTIES_COUNT + CORRECT_US_TERRITORIES_COUNTIES_COUNT
if found_total_counties == correct_counties_count:
    print(f'[OK ] Found {found_total_counties} counties - correct')
else:
    print(f'[ERR] Found {found_total_counties} counties - incorrect (should be {correct_counties_count} <- '
          f'{CORRECT_US_STATES_COUNTIES_COUNT} + {CORRECT_US_TERRITORIES_COUNTIES_COUNT})')
    sys.exit(1)
