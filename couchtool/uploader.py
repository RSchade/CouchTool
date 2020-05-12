import urllib.parse as urlparse
from hashlib import md5
import requests
from sys import exit

# uploads documents to couchdb in the format given by directoryparser
def upload_parsed_directory_tree(baseurl : str, documents : dict, force : bool):
    for db in documents:
        for doc in documents[db]:
            doc_url = urlparse.urljoin(baseurl, db + "/" + doc["_id"])
            retry = True
            while retry == True:
                # upload doc to doc_url
                res = requests.put(doc_url, json=doc)
                if res.status_code == 404:
                    print("404 error recieved, are you sure database", db, "exists?")
                    return
                elif res.status_code == 401:
                    print("Unauthorized, are you sure the username and password supplied are correct?")
                    return
                elif res.status_code == 409:
                    # _rev error, if the md5 hashes are different we reupload with an updated _rev
                    res = requests.get(doc_url)
                    online_doc = res.json()
                    if ("digest" in online_doc and online_doc["digest"] != doc["digest"]) or force == True:
                        # reupload
                        print("Updating document in database", db,
                              "with id", doc["_id"], "on server revision", online_doc["_rev"])
                        doc["_rev"] = online_doc["_rev"]
                    else:
                        print("Conflict with online version of", doc["_id"], 
                              "in database", db, "and the offline copy")
                        if "digest" not in online_doc:
                            print("Digest doesn't exist online, must have been inserted by a different tool")
                        else:
                            print("Digests are the same, no update needed")
                        retry = False
                elif res.status_code == 400:
                    print("Error uploading, aborting")
                    print(doc)
                    print(res.json())
                    return
                else:
                    print("Uploaded document with id", doc["_id"], "to database", db)
                    print(res.json())
                    retry = False

def create_databases(baseurl: str, dbs : list):
	for db in dbs:
		print("Creating database", db)
		res = requests.put(urlparse.urljoin(baseurl, db))
		print(res.json())
		if res.status_code == 201 or res.status_code == 202:
			print("Database", db, "created")
		elif res.status_code == 400:
			print("Invalid database name", db, "quitting...")
			exit(1)
		elif res.status_code == 401:
			print("Unauthorized to create", db, "quitting...")
			exit(1)
		elif res.status_code == 412:
			print("Database", db, "already exists, continuing...")
