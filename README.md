# CouchTool

Allows easy uploading and downloading CouchDB design documents.

## Usage

usage: CouchTool [-h] --url url --project project folder [--force] [--pretend]
                 [--create-databases] [--language language]
                 (--upload | --download)

Automated CouchDB configuration uploader

optional arguments:
  -h, --help            show this help message and exit
  --url url             URL of the CouchDB database, with admin credentials
                        and the port. Example:
                        http://uname:password@someserver.com:5984/
  --project project folder
                        Project folder to use to either upload or download the
                        configuration
  --force               Specifies to force an upload of the configuration,
                        even if they aren't different
  --pretend             Pretends to upload, prints the JSON to the console
  --create-databases    Creates target databases if they do not exist when
                        uploading
  --language language   Language for the design document, only for uploading
  --upload              Specifies to upload the project folder to CouchDB
  --download            Specifies to use the specific database targeted by the
                        URL, downloading its configuration into the project
                        folder

## Installation

Either install editable with 'pip3 install -e CouchTool' or build the wheel file with 'setup.py bdist_wheel' and then install the wheel file.