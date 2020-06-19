# [TISTA Science & Technology Corporation](https://tistatech.com) Data Repository

The repository contains open data that Tista company uses in its own projects.

All of the result static files located on the public Tista storage: [data.tistatech.com/common/v1/](https://data.tistatech.com/common/v1/index.html).

## Requirements

* Linux base system
* Python 3.8+
* jq, curl, csvtojson


## Development

### Code structure
* ```common```                  - main diretory with all static files
    - ```us```                  - US specific data files
    - ```countries.csv```       - list of all countries
    - ```population.csv```      - list of all populations by countries
    - ```index.html```          - web page with simple documentation about all files in the *common* directory
* ```scripts```                 - devops and helper scripts for the project
*   - ```converter```           - scripts to convert files to different formats and types
*   - ```devops```              - scripts to build/deploy files to the static hosting
*   - ```load-data```           - scripts to prepare static data files inside the *common* directory
* ```index.html, styles.css```  - main files for static website

### Build and Deploy

1. Generate all static files for web site:
```bash
./scripts/devops/build-common-data.sh
```
All files will be generated inside the ```./build/common/v1``` directory.

2. Deploy/Upload the result files to the remote AWS S3 bucket:
```bash
S3_BUCKET=data-dev.tistatech.com ./scripts/devops/upload-common-data-to-s3-bucket
```
All files from the ```./build/common/v1``` will be uploaded to the ```s3://data-dev.tistatech.com/common/v1```.

You can use system environment variables to customize deploy process:
| name              | description | 
| ----------------- | ---------------------------------- |
| ```CACHE_MAX_AGE``` | Set ```Cache-Control: max-age=86400``` http header value for all uploaded files on S3 bucket. Default: ```CACHE_MAX_AGE=86400``` (24 hours) |
| ```VERSION```       | Set target directory version. Default value is ```1``` -> ```/common/v1``` |


## Data sources

* Coordinates
    - [Google Public Dataset](https://developers.google.com/public-data)
    - [Census.org - Cartographic Boundary Files](https://www2.census.gov/geo/tiger/GENZ2010/)
* Countries:
    - [Wikipedia ISO 3166-1 page](https://en.wikipedia.org/wiki/ISO_3166-1#Officially_assigned_code_elements)

## License

The source code inside this repository are licensed under the [Apache 2.0 License](/LICENSE) and 
the data content is licensed under the [Creative Commons Attribution-ShareAlike 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/).