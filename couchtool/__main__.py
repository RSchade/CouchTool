import argparse
import couchtool.directoryparser as dirparser
import couchtool.uploader as uploader
import couchtool.downloader as downloader
from urllib.parse import urlparse
from os.path import basename, join
from sys import exit

parser = argparse.ArgumentParser(prog="CouchTool", description="Automated CouchDB configuration uploader")
parser.add_argument("--url", metavar="url", type=str, nargs=1, required=True,
                    help="URL of the CouchDB database, with admin credentials and the port. " +
                    "Example: http://uname:password@someserver.com:5984/")
parser.add_argument("--project", metavar="project folder", type=str, nargs=1, required=True,
                    help="Project folder to use to either upload or download the configuration")

parser.add_argument("--force", action='store_true',
                    help="Specifies to force an upload of the configuration, even if they aren't different")
parser.add_argument("--pretend", action='store_true',
                    help="Pretends to upload, prints the JSON to the console")
parser.add_argument("--create-databases", action='store_true',
                    help="Creates target databases if they do not exist when uploading")
parser.add_argument("--language", metavar="language", type=str, nargs=1, required=False,
                    help="Language for the design document, only for uploading")

upordownload = parser.add_mutually_exclusive_group(required=True)
upordownload.add_argument("--upload", action='store_true',
                    help="Specifies to upload the project folder to CouchDB")
upordownload.add_argument("--download", action='store_true',
                    help="Specifies to use the specific database targeted by the URL"+
                    ", downloading its configuration into the project folder")

args = vars(parser.parse_args())

url = args["url"][0]

if args["upload"] == True:
    language = "javascript"
    if args["language"] is not None:
        language = args["language"][0]
    dir_tree_obj = dirparser.read_directory_tree(args["project"][0], language)
    if args["create_databases"] == True:
        uploader.create_databases(url, list(dir_tree_obj.keys()))
    if args["pretend"]:
        print(dir_tree_obj)
    else:
        uploader.upload_parsed_directory_tree(url, dir_tree_obj, args["force"])
elif args["download"] == True:
    if args["create_databases"] == True:
        print("Create databases should only be set for uploading")
        exit(1)
    db_name =  basename(urlparse(url).path)
    if db_name == None:
        print("No database specified, quitting...")
    else:
        downloader.download_database_config(url, join(args["project"][0], db_name), args["pretend"])
