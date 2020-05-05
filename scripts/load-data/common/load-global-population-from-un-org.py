#!/usr/bin/env python3
# #############################################################################
# Helper script to generate world/population.csv file
# * Download population data from population.un.org
#
# #############################################################################
import codecs
import csv
import datetime
import os
import urllib.request as request
from pathlib import Path


# -----------------------------------------------------------------------------
# Show debug output only with the env.DEBUG = true
debug = lambda msg: print(msg) if os.environ.get('DEBUG') == 'true' else lambda msg: None


# -----------------------------------------------------------------------------
def find_country(src_country_name):
    # Create special name1 and name2 for search
    name1 = src_country_name.lower()
    # Skip non country records
    if 'dependenc' in name1 or 'fed. states of' in name1:
        return None
    name1 = src_country_name.lower().split('(')[0].strip()
    name2 = None
    if src_country_name in custom_mapping or {}:
        name2 = custom_mapping[src_country_name]
    elif name1.startswith('republic of'):
        name2 = name1[11:].strip()
    for (c_id, c_name, c_aliases) in countries:
        # check name1 and name2 with real county name or witj aliases
        if name1 and (name1 == c_name.lower() or name1 in c_aliases) \
                or name2 and (name2 == c_name.lower() or name2 in c_aliases):
            return (c_id, c_name)
    return None


# -----------------------------------------------------------------------------
# Load all countries from the countries.csv into the list (country_id, country_name, country_aliases)
countries_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'countries.csv'
print(f'Read csv with countries: {countries_file}')
countries = []
for r in csv.reader(countries_file.open('r'), delimiter=',', quotechar='"'):
    aliases = [a.strip() for a in (r[7] or '').lower().split(';')]
    aliases.append((r[4] or '').lower().strip())
    item = (r[0], r[3], [a for a in aliases if a])
    countries.append(item)
countries.pop(0)                        # remove header

# -----------------------------------------------------------------------------
# Hardcoded countries names special for the population.un.org
custom_mapping = {
    'Democratic Republic of the Congo': 'congo',
    'Dem. People\'s Republic of Korea': 'north korea',
    'China, Taiwan Province of China': 'taiwan',
    'China, Hong Kong SAR': 'hong kong',
    'China, Macao SAR': 'macau',
    'Lao People\'s Democratic Republic': 'laos'
}

# -----------------------------------------------------------------------------
cur_year = datetime.datetime.now().year
output_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'population.csv'
src_url = 'https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv'
# src_url = f'file://{Path(__file__).parent.resolve()}/WPP2019_TotalPopulationBySex.csv'
found_population = []

print(f'Read csv file from: {src_url}')
csv_reader = csv.reader(codecs.iterdecode(request.urlopen(src_url), 'utf-8'), delimiter=',', quotechar='"')
print(f'Read file with population line by line')
# LocID,Location,VarID,Variant,Time,MidPeriod,PopMale,PopFemale,PopTotal,PopDensity
for (loc_id, country_name, var_id, variant, year, _, _, _, population, _) in csv_reader:
    if loc_id == 'LocID' or year != f'{cur_year}' or variant.lower() != 'medium':
        continue            # skip header and select only current year
    country = find_country(country_name)
    if country:
        population = int(float(population) * 1000)
        debug(f'{country[0]},{country[1]},{population}')
        found_population.append((country[0], country[1], population))
    else:
        debug(f'Can\'t find country: {country_name}. Skip.')

counter_success = len(found_population)
# Add countries to the result list which are not found in population list
found_country_ids = [i[0] for i in found_population]
for (country_id, country_name, _) in [c for c in countries if c[0] not in found_country_ids]:
    print(f'Warning: [{country_id}] {country_name} - A population not found.')
    found_population.append((country_id, country_name, None))

# Write result to the csv file
with output_file.open('w') as file_writer:
    csv_writer = csv.writer(file_writer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['id', 'name', f'population'])
    for item in sorted(found_population, key=lambda x: x[0]):
        csv_writer.writerow(item)

print(f'Complete: {counter_success} countries with population, {len(found_population)} counties saved')
print(f'Result file is {output_file}')
