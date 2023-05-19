
# iRODS collection downloader 

import argparse, pathlib

from irods.collection import iRODSCollection, iRODSDataObject
from irods.session import iRODSSession
from irods.ticket import Ticket
from irods.models import Collection

aparser = argparse.ArgumentParser(
    prog = 'irods-fetch',
    description = 'LIMS utility for downloading collection of files from iRODS cloud',
    epilog = ''
)

aparser.add_argument("--ticket", "-t", dest="ticket", help="Access ticket")

aparser.add_argument("--host", required=True, dest="host", help="iRODS host")
aparser.add_argument("--port", "-p", dest="port", type=int, default="1247", help="iRODS port")
aparser.add_argument("--user", "-u", dest="user", default="anonymous", help="iRODS user")
aparser.add_argument("--password", "-P", dest="password", default="", help="iRODS user password")

aparser.add_argument("--collection", "-c", required=True, dest="collection_path", type=pathlib.Path, help="Collection path")
aparser.add_argument("--output_dir", "-o", dest="output_dir", type=pathlib.Path, default=pathlib.Path("."))

arguments = aparser.parse_args()

# Extract zone from the collection argument (first path part)
arguments.zone = arguments.collection_path.parents[-2].stem 

# Open iRODS session
with iRODSSession(port=arguments.port, host=arguments.host, user=arguments.user, password=arguments.password, zone=arguments.zone) as irods_session:
    
    # -------- grent ticket
    # new_t = Ticket(irods_session)
    # new_t.issue("read", arguments.collection_path)
    # print(new_t.string)
    # exit()
    # -------

    # Supply the access ticket, if any 
    if arguments.ticket:
        Ticket(irods_session, arguments.ticket).supply()
        # collection = iRODSCollection(irods_session.collections, irods_session.query(Collection).one())
    #else:
    #    collection = irods_session.collections.get(arguments.collection_path)

    
    #irods_session.query()
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