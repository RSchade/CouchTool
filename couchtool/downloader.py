import urllib.parse as urlparse
import requests
import json
from os import makedirs
from os.path import join, dirname, basename

def download_database_config(url : str, path : str, pretend : bool):
    # create the directory if it doesn't exist
    makedirs(path, exist_ok=True)
    # get all design documents
    all_design_url = url + "/_all_docs?start_key=\"_design\"&end_key=\"_design\ufff0\"&include_docs=true"
    res = requests.get(all_design_url)
    design_docs = res.json()["rows"]
    for row in design_docs:
        cur_ddoc = row["doc"]
        del cur_ddoc["_rev"]
        # create a directory for the ddoc
        ddoc_name = cur_ddoc["_id"].split("/")[1]
        cur_path = join(path, ddoc_name)
        # create directory trees for all of the attributes with dictionaries under them
        if "language" not in cur_ddoc or cur_ddoc["language"] != "query":
            # regular design document
            makedirs(cur_path, exist_ok=True)
            create_dir_tree_from_dicts(cur_ddoc, cur_path)
        else:
            # if it's a query language, then just save the json
            with open(cur_path, 'w') as file:
                    file.write(json.dumps(cur_ddoc)) 
            print("Wrote query design doc", ddoc_name)
        # download all of the attachments and put them in the directory
        if "_attachments" in cur_ddoc:
            for att_name in cur_ddoc["_attachments"].keys():
                res = requests.get(url + "/" + cur_ddoc["_id"] + "/" + att_name)
                # handle the special case where the attachment is a path. Create all of the
                # subdirectories leading to that path.
                att_relative_path = dirname(att_name)
                att_full_path = join(cur_path, att_relative_path)
                makedirs(att_full_path, exist_ok=True)
                with open(join(att_full_path, condition_att_name(att_name)), 'wb') as file:
                    file.write(res.content)
                print("Wrote attachment", att_name)

file_reserved = ["<", ">", ":", "\"", "\\", "/", "|", "?", "*", "\x00"]

# remove special characters, replace with -
def condition_att_name(name):
    name = basename(name)
    if name[0] == "_":  # _ at the beginning isn't allowed
       name = name.replace("_", "-", 1)
    for special in file_reserved:
       name = name.replace(special, "-")
    return name

no_write = ["_id", "_rev", "language", "digest", "_attachments", "couchapp"]

def create_dir_tree_from_dicts(obj : dict, path: str):
    for key in obj:
        if key not in no_write:
            if type(obj[key]) is dict:
                cur_path = join(path, key)
                makedirs(cur_path, exist_ok=True)
                create_dir_tree_from_dicts(obj[key], cur_path)
            else:
                print("Writing document with key", key)
                with open(join(path, key), 'wb') as file:
                    file.write(str(obj[key]).encode("utf-8")) 