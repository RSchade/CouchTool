from os import listdir, walk, sep
from os.path import isfile, join, basename, split, normpath, splitext
import json
import mimetypes
from hashlib import md5
import base64
import pickle

mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/font-woff", ".woff")
mimetypes.add_type("text/plain", "")

# reads file and creates md5 hash of it
# stores the hash alongside with a .md5 extension
def read_file(path : str):
    with open(path, 'r', encoding="utf-8") as file:
        file_data = file.read()
        digest = md5(file_data.encode("utf-8")).hexdigest()
        return (file_data, digest)

def file_name_no_ext(path : str):
    return basename(path).split(".")[0]

def file_name_to_att(att_file_path : str, att_file_name : str):
    att_obj = {}
    with open(att_file_path, "rb") as file:
        text = file.read()
        base64_att = base64.b64encode(text).decode()
        att_obj["data"] = base64_att
        filetype, _ = mimetypes.guess_type(att_file_path)
        if filetype is None:
            filetype = "application/octet-stream"
        att_obj["content_type"] = filetype
    return att_obj

# adds as an attachment if necessary or as an attribute or json encoded attribute
# ddoc_section is the section to add the text attachments to
# attachments_section is the _attachments section of the design doc
# dirpath is the full path to this file
# upload_path is the path to add to the attachments section for this file
def add_as_correct_att(ddoc_section : object, attachments_section: object, att_file_name : str, dirpath : str, upload_path : str):
    att_file_path = join(dirpath, att_file_name)
    filetype, _ = mimetypes.guess_type(att_file_path)
    if filetype != None and ("application/json" in filetype or "text/plain" in filetype):
        with open(att_file_path, "r", encoding="utf-8") as file:
            data = file.read()
            data_name = file_name_no_ext(att_file_name)
            try:
                data_as_json = json.loads("{\"data\":"+data.replace("\'", "\"")+"}")
                ddoc_section[data_name] = data_as_json["data"]
            except Exception as e:
               ddoc_section[data_name] = data
    else:
        upload_path = upload_path.replace("\\", "/")
        if upload_path != "":
            upload_path = upload_path + "/"
        attachments_section[upload_path + att_file_name] = file_name_to_att(att_file_path, att_file_name)

# reads a directory tree and creates required documents
def read_directory_tree(path : str, language : str):
    to_upload = {}
    path = normpath(path)
    base_dir_level = len(path.split(sep))
    # walk through the tree
    # these are changed when traversing the tree,
    # since the tree is traversed down we will not visit a
    # new database, design document, or design document category
    # without being done with the previous
    cur_db_name = None
    cur_ddoc = None
    category_name = None
    def add_ddoc_if_needed():
        if cur_ddoc is not None:
            cur_ddoc["digest"] = md5(pickle.dumps(cur_ddoc)).hexdigest()
            to_upload[cur_db_name].append(cur_ddoc)
    for file in walk(path, topdown=True, followlinks=True):
        (dirpath, dirnames, filenames) = file
        # get the level in the file tree
        cur_level = len(dirpath.split(sep)) - base_dir_level
        cur_name = basename(dirpath)
        if cur_level == 0:
            # project level
            pass
        elif cur_level == 1:
            # databases
            add_ddoc_if_needed()
            cur_ddoc = None
            cur_db_name = cur_name # set the database name
            to_upload[cur_name] = []
            # load in the document files that need to be uploaded
            for db_file_name in filenames:
                (file_data, digest) = read_file(join(dirpath, db_file_name))
                couch_file = json.loads(file_data)
                couch_file["digest"] = digest
                to_upload[cur_db_name].append(couch_file)
        elif cur_level == 2:
            # design document folders
            # create the digest of the design document that went before this, if it exists
            add_ddoc_if_needed()
            cur_ddoc = {
                    "_id": "_design/" + cur_name, 
                    "language": language, 
                    "_attachments": {}
                }
            # load in the attachments that need to be uploaded with this design doc
            # as well as the categories that are single files (with special names)
            for att_file_name in filenames:
                add_as_correct_att(cur_ddoc, cur_ddoc["_attachments"], 
                    att_file_name, dirpath, "")
        elif cur_level == 3:
            # design document categories
            category_name = cur_name
            # upload any single file categories as attachments if they don't look like text
            for att_file_name in filenames:
                if category_name not in cur_ddoc:
                    cur_ddoc[category_name] = {}
                add_as_correct_att(cur_ddoc[category_name], cur_ddoc["_attachments"], 
                    att_file_name, dirpath, category_name)
                if cur_ddoc[category_name] == {}:
                    del cur_ddoc[category_name]
        elif cur_level == 4:
            # inside design document categories
            if category_name not in cur_ddoc:
                cur_ddoc[category_name] = {}
            cur_ddoc[category_name][cur_name] = {}
            # add in the files that make up this category
            for att_file_name in filenames:
                add_as_correct_att(cur_ddoc[category_name][cur_name], cur_ddoc["_attachments"],
                    att_file_name, dirpath, category_name + "/" + cur_name)
            """for att_file_name in filenames:
                att_file_path = join(dirpath, att_file_name)
                with open(att_file_path, "r") as att_file:
                    cur_ddoc[category_name][cur_name][file_name_no_ext(att_file_name)] = att_file.read()
            """
        else:
            # unsupported, even deeper directory structure
            print("Unsupported directory found", dirpath)
    # add the last remaining design document to the last database, if there is one
    add_ddoc_if_needed()
    return to_upload