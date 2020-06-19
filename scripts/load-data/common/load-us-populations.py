#!/usr/bin/env python3
# #############################################################################
# Helper script to load US population from census.gov
# Save result into the '../../common/us/population.csv' file
#
# #############################################################################
import codecs
import csv
import os
import sys
from urllib import request
from pathlib import Path

codecs.register_error('strict', codecs.ignore_errors)
URL = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv'
# URL = f'file://{(Path(__file__).parent / "co-est2019-alldata.csv").resolve()}'
CORRECT_US_STATES_COUNTIES_COUNT = 3143                        # value on end 2017
STATES_US_COUNT = 51
output_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'population.csv'
population_list = []

# -----------------------------------------------------------------------------
# Show debug output only with the env.DEBUG = true
debug = lambda msg: print(msg) if os.environ.get('DEBUG') == 'true' else lambda msg: None


# -----------------------------------------------------------------------------
# Load all states (state_id, state_fips, state_name}
states_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'states.csv'
print(f'Read csv with states: {states_file}')
states = [(r[0], r[1], r[2].lower()) for r in csv.reader(states_file.open('r'), delimiter=',', quotechar='"')]
search_state_by_name = lambda val: ([x for x in states if x[2] == val] or [None])[0]
debug(f'Loaded {len(states)} states')

# -----------------------------------------------------------------------------
# Load all counties {fips, state_id, county_name)}
counties_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'counties.csv'
print(f'Read csv with counties: {counties_file}')
counties = [(r[0], r[1], r[2]) for r in csv.reader(counties_file.open('r'), delimiter=',', quotechar='"')]
search_county_by_fips = lambda val: ([x for x in counties if x[0] == val] or [None])[0]
debug(f'Loaded {len(counties)} counties')


# -----------------------------------------------------------------------------
# Add values to the main result list
def add_to_population_list(state_id, fips, population, state_fips):
    print(f'Processing: State={state_id}/{state_fips}, Fips={fips}, Population={population}')
    population_list.append([state_id, fips, population, state_fips])


print(f'Load data from {URL}')
stream = codecs.iterdecode(request.urlopen(URL), 'utf-8', errors='backslashreplace')
csv_reader = csv.reader(stream, delimiter=',', quotechar='"')
print(f'Read file with population line by line')
# We need: #3 - fips_up, #4 - fips_low, #5 - state_name, #6 - county_name, #$18 - population

for row in csv_reader:
    try:
        debug(f'Processing RAW: {row}')
        fips_up = row[3].lower()
        fips_low = row[4].lower()
        if not row or len(row) <= 18 or row[0] == 'SUMLEV':
            continue                        # skip header
        if fips_low == '000':
            fips = f'{fips_low}{fips_up}'.rjust(5, '0')
        elif fips_low and fips_up:
            fips = f'{fips_up}{fips_low}'.rjust(5, '0')
        if fips in ['02093', '02261']:
            debug('Skip: Valdez–Cordova Census Area (Alaska) - on Jan 2019')
            continue
        state_name = row[5].lower()
        state = search_state_by_name(state_name.lower())
        state_id = state[0] if state else None
        state_fips = state[1] if state else 0
        county_name = row[6].replace('\'', '').lower()
        county = row[6].replace('\'', '').lower()
        population = int(row[18])
        add_to_population_list(state_id, fips, population, state_fips.rjust(2, '0'))
    except Exception as ex:
        print(f'Error processing row: {row}')
        debug(f'Exception: {ex}')

# Correction on 2020
# https://censusreporter.org/profiles/06000US0226114420-chugach-census-subarea-valdez-cordova-census-area-ak/
add_to_population_list('AK', '02063', 7372, '02')
# https://censusreporter.org/profiles/06000US0226117350-copper-river-census-subarea-valdez-cordova-census-area-ak/
add_to_population_list('AK', '02066', 1929, '02')

counties_count = 0
states_count = 0
with output_file.open('w') as file_writer:
    csv_writer = csv.writer(file_writer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['state_id', 'fips', 'population'])
    for item in sorted(population_list, key=lambda x: (x[3], x[1])):
        if item[1].startswith('000'):
            states_count += 1
        else:
            counties_count += 1
        csv_writer.writerow([item[0], item[1], item[2]])

print(f'Done: processed {states_count} states, {counties_count} counties')
has_error = False
if CORRECT_US_STATES_COUNTIES_COUNT == counties_count:
    print(f'[OK ] Found {counties_count} counties - correct')
else:
    print(f'[ERR] Found {counties_count} counties - incorrect (should be {CORRECT_US_STATES_COUNTIES_COUNT})')
    has_error = True
if STATES_US_COUNT == states_count:
    print(f'[OK ] Found {states_count} states - correct')
else:
    print(f'[ERR] Found {states_count} states - incorrect (sould be {STATES_US_COUNT})')
    has_error = True
sys.exit(1 if has_error else 0)
