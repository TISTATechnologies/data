#!/usr/bin/env python3
# #############################################################################
# Convert zips.csv file into the directory with the zips splitted by zone in csv files.
#
# Usage: create-us-zips-cache-directory [output]
#   output - directory where "zips" directory will be created (default: current)
# Example:
#   All 208xx zips will be copied into the /2/208.csv file
#
# #############################################################################
import codecs
import csv
import os
import sys
from urllib import request
from pathlib import Path


# -----------------------------------------------------------------------------
# Show debug output only with the env.DEBUG = true
debug = lambda msg: print(msg) if os.environ.get('DEBUG') == 'true' else lambda msg: None


# -----------------------------------------------------------------------------
# rm dir recursively
def rm_tree(full_path: Path):
    for child in full_path.glob('*'):
        if child.is_file():
            debug(f'Delete file: {child}')
            child.unlink()
        else:
            rm_tree(child)
    debug(f'Delete directory: {child}')
    full_path.rmdir()


# -----------------------------------------------------------------------------
# Load all counties {fips, state_id, county_name)}
counties_file = Path(__file__).parent / '..' / '..' / 'common' / 'us' / 'counties.csv'
debug(f'Read csv with counties: {counties_file}')
counties = [(r[0], r[1], r[2]) for r in csv.reader(counties_file.open('r'), delimiter=',', quotechar='"')]
search_county_by_fips = lambda val: ([x for x in counties if x[0] == val] or [None])[0]
print(f'Loaded {len(counties)} counties')


# -----------------------------------------------------------------------------
# Load all zips {zip, fips)}
zips_file = Path(__file__).parent / '..' / '..' / 'common' / 'us' / 'zips.csv'
debug(f'Read csv with zips: {zips_file}')
zips = [(r[0], r[1]) for r in csv.reader(zips_file.open('r'), delimiter=',', quotechar='"')]
print(f'Loaded {len(zips)} zips')


arg1 = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
root_output = Path(arg1).resolve()
print(f'Output directory {root_output}')
if root_output.exists():
    print(f'Remove old data in the directory{root_output}')
    rm_tree(root_output)
zips_with_info = {}
print(f'Processing {len(zips)} zips (please wait)...')
for (zip, fips) in zips:
    if not zip.isdigit():
        continue                # skip header
    county = search_county_by_fips(fips)
    file_name = f'{zip[0:1]}/{zip[0:3]}'
    debug(f'Output file {file_name}')
    if file_name not in zips_with_info:
        zips_with_info[file_name] = {}
    if zip not in zips_with_info[file_name]:
        zips_with_info[file_name][zip] = []
    zips_with_info[file_name][zip].append({
        'fips': county[0],
        'name': county[2],
        'state_id': county[1]
    })
    debug(f'{file_name} = {county}')

minify = os.environ.get('MINIFY') == 'true'
for (file_name, zips) in zips_with_info.items():
    output_file_csv = root_output / (file_name + '.csv')
    debug(f'Creating {output_file_csv} with {len(zips)} zips...')
    output_file_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_file_csv.open('w') as fo:
        csv_writer = csv.writer(fo, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['zip', 'fips', 'name', 'state_id'])
        for zip in zips:
            for county in zips[zip]:
                csv_writer.writerow([zip, county['fips'], county['name'], county['state_id']])
    print(f'Create {output_file_csv} with {len(zips)} zips - complete.')

print(f'Result directory: {root_output}')
