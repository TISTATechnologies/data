#!/usr/bin/env python3
# #############################################################################
# Helper script to generate us-zips.csv file
# * Source: huduser.gov
# * Source: usps.com (online tool to check zip validation)
# Save result into the '../../common/us/zips.csv' file
#
# requirements: pandas, xlrd
# #############################################################################
import codecs
import csv
import os
import pandas
from pathlib import Path
from urllib import request, parse as urlparse

codecs.register_error('strict', codecs.ignore_errors)
output_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'zips.csv'

# -----------------------------------------------------------------------------
# Show debug output only with the env.DEBUG = true
debug = lambda msg: print(msg) if os.environ.get('DEBUG') == 'true' else lambda msg: None


# -----------------------------------------------------------------------------
# Load all counties {fips, state_id, county_name)}
counties_file = Path(__file__).parent / '..' / '..' / '..' / 'common' / 'us' / 'counties.csv'
print(f'Read csv with counties: {counties_file}')
counties = [(r[0], r[1], r[2]) for r in csv.reader(counties_file.open('r'), delimiter=',', quotechar='"')]
search_county_by_fips = lambda val: ([x for x in counties if x[0] == val] or [None])[0]
debug(f'Loaded {len(counties)} counties')
fips_remap = {
    '46113': '46102',       # Shannon County -> Oglala Lakota County
    '02270': '02158',       # Wade Hampton Census Area -> Kusilvak Census Area
    '02261': '02063'        # Valdez-Cordova Census Area -> Chugach Census Area
}


def zip_validation_usps(zip):
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'User-Agent': 'MozillaChrome'}
    post_url = 'https://tools.usps.com/tools/app/ziplookup/cityByZip'
    debug(f'Check {zip} with usps online tool')
    post_data = (f'zip={zip}').encode('utf-8')
    req = request.Request(post_url, headers=headers)
    resp = request.urlopen(req, data=post_data)
    resp_data = resp.read().decode('utf-8')
    debug(f'Response: {resp_data}')
    success = 'SUCCESS' in resp_data
    return success


def load_zips_from_huduser():
    URL = 'https://www.huduser.gov/portal/datasets/usps/ZIP_COUNTY_032020.xlsx'
    # URL = f'file://{(Path(__file__).parent / "ZIP_COUNTY_032020.xlsx").resolve()}'
    print(f'Download data from: {URL}')
    data = pandas.read_excel(URL, sheet_name=0, columns='A,B')
    res_zips = []
    print(f'Read data line by line')
    idx = 0
    for row in data.itertuples():
        debug(f'[{idx:05}] Processing {row}...')
        zip = f'{row[1]:05}'
        fips = f'{row[2]:05}'
        debug(f'ZIP = {zip}, FIPS = {fips}')
        county = search_county_by_fips(fips)
        if not county:
            if zip_validation_usps(zip):
                new_fips = fips_remap.get(fips)
                if new_fips:
                    print(f'[WAR] Fips {fips} not found. Zip code {zip} is valid! Remapping to {new_fips}')
                    county = [new_fips]
                else:
                    print(f'[ERR] Fips {fips} not found. Zip code {zip} is valid!')
            else:
                print(f'[ERR] Fips {fips} not found. Zip code {zip} invalid')
        if county and county[0] is not None:
            print(f'[OK ] {zip} -> {fips}')
            res_zips.append((zip, county[0]))
            idx += 1
    return res_zips


with output_file.open('w') as file_writer:
    csv_writer = csv.writer(file_writer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['zip', 'fips'])
    zips = load_zips_from_huduser()
    print(f'Found {len(zips)} zips')
    for zip, fips in sorted(zips, key=lambda x: (x[0], x[1])):
        debug(f'Write {zip}, {fips}')
        csv_writer.writerow([zip, fips])
    print(f'Write {len(zips)} zips with fips into the file {output_file}')
