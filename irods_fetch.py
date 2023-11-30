
# iRODS collection downloader 

import argparse, pathlib
import tempfile

from irods.collection import iRODSCollection
from irods.session import iRODSSession
from irods.ticket import Ticket
import re

import urllib3

aparser = argparse.ArgumentParser(
    prog = 'irods-fetch',
    description = 'LIMS utility for downloading collection of files from iRODS cloud'
)

aparser.add_argument("--ticket", "-t", dest="ticket", help="Access ticket")

aparser.add_argument("--host", required=True, dest="host", help="iRODS host")
aparser.add_argument("--port", "-p", dest="port", type=int, default="1247", help="iRODS port, defaults to 1247")
aparser.add_argument("--user", "-u", dest="user", default="anonymous", help="iRODS user, defaults to 'anonymous'")
aparser.add_argument("--password", "-P", dest="password", default="", help="iRODS user password, defaults to empty password")

aparser.add_argument("--collection", "-c", required=True, dest="collection_path", type=pathlib.Path, help="Collection path")
aparser.add_argument("--output_dir", "-o", dest="output_dir", type=pathlib.Path, default=pathlib.Path("."))

# Cert / Auth
aparser.add_argument("--authentication_scheme", dest="authentication_scheme", type=str, default="PAM")
aparser.add_argument("--ssl_verify_server", dest="ssl_verify_server", type=str, default="cert")
aparser.add_argument("--ssl_ca_certification_file", dest="ssl_ca_certification_file", type=str, default="https://pki.cesnet.cz/_media/certs/chain_geant_ov_rsa_ca_4_full.pem")
aparser.add_argument("--encryoption_algorithm", dest="encryoption_algorithm", type=str, default="AES-256-CBC")
aparser.add_argument("--encryption_key_size", dest="encryption_key_size", type=int, default=32)
aparser.add_argument("--encryption_num_hash_rounds", dest="encryption_num_hash_rounds", type=int, default=16)
aparser.add_argument("--encryption_salt_size", dest="encryption_salt_size", type=int, default=8)

arguments = aparser.parse_args()

# Resolve SSL file - can be url 
if arguments.ssl_ca_certification_file and re.match(r'^https?://', arguments.ssl_ca_certification_file):
    # Its url - download it to temporary file
    with urllib3.request.urlopen(arguments.ssl_ca_certification_file) as response:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write the content of the URL to the temporary file
            temp_file.write(response.read())
            arguments.ssl_ca_certification_file = temp_file.name

# Extract zone from the collection argument (first path part)
arguments.zone = arguments.collection_path.parts[1] 

# Open iRODS session
with iRODSSession(**arguments) as irods_session:
    
    # -------- grent ticket
    new_t = Ticket(irods_session)
    new_t.issue("read", arguments.collection_path)
    # print(new_t.string)
    # exit()
    # -------

    # Supply the access ticket, if any 
    if arguments.ticket:
        Ticket(irods_session, arguments.ticket).supply()
        # collection = iRODSCollection(irods_session.collections, irods_session.query(Collection).one())
        #irods_session.query()
    #else:
    #    collection = irods_session.collections.get(arguments.collection_path)

    
    collection = irods_session.collections.get(str(arguments.collection_path))

    print(f"Connected to iRODS, starting file downloads from the collection {collection.path}...")

    def walk_collection(collection: iRODSCollection):
        for subcol in collection.subcollections:
            yield from walk_collection(subcol) # Recurse into subcollections
        
        for dobj in collection.data_objects:
            yield dobj

    data_objects = list(walk_collection(collection))
    total_files = len(data_objects)
    current_file = 0

    # Download collection files
    for data_obj in data_objects:
        target_path: pathlib.Path = arguments.output_dir / pathlib.Path(data_obj.path).relative_to(arguments.collection_path) 

        # Check if file already exists and has same size as collection file
        # In that case, skip it
        if target_path.exists():
            # File already there - does it have the same size?
            if target_path.stat().st_size == data_obj.size:
                # Skip - it is already downloaded
                print(f"[{current_file+1}/{total_files}] Skipped file {target_path} - already downloaded")
                current_file = current_file + 1
                continue
            else: 
                target_path.unlink(missing_ok=True)
        
        # Ensure directory exists for the target file
        if not target_path.parent.is_dir():
            target_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        print(f"[{current_file+1}/{total_files}] Downloading file {str(target_path)}...")
        irods_session.data_objects.get(data_obj.path, str(target_path))
        current_file = current_file + 1

# iRODS session closed

print(f"Successfully downloaded collection: {arguments.collection_path}")