
# iRODS collection downloader 

import argparse, pathlib

from irods.collection import iRODSCollection
from irods.session import iRODSSession
from irods.ticket import Ticket

import time

# Utility to convert file size to huma readable format
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


aparser = argparse.ArgumentParser(
    prog = 'irods-fetch',
    description = 'LIMS utility for downloading collection of files from iRODS cloud'
)

aparser.add_argument("--ticket", "-t", dest="ticket", help="Access ticket")

aparser.add_argument("--host", required=True, dest="host", help="iRODS host")
aparser.add_argument("--port", "-p", dest="port", type=int, default="1247", help="iRODS port, defaults to 1247")
aparser.add_argument("--user", "-u", dest="user", default="anonymous", help="iRODS user, defaults to 'anonymous'")
aparser.add_argument("--password", "-P", dest="password", default="", help="iRODS user password, defaults to empty password")

aparser.add_argument("--collection", "-c", required=True, dest="collection_path", type=pathlib.PurePosixPath, help="Collection path")
aparser.add_argument("--output_dir", "-o", dest="output_dir", type=pathlib.Path, default=pathlib.Path("."))
aparser.add_argument("--sleep_time", "-s", dest="sleep_time", type=float, default=20, help="Sleep time in seconds between scans, defaults to 20 sec")

arguments = aparser.parse_args()

# Extract zone from the collection argument (first path part)
arguments.zone = arguments.collection_path.parts[1] 

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
       
    collection = irods_session.collections.get(str(arguments.collection_path))
    print(f"Connected to iRODS, starting file downloads from the collection {collection.path}...")

    def walk_collection(collection: iRODSCollection):
        for subcol in collection.subcollections:
            yield from walk_collection(subcol) # Recurse into subcollections
        
        for dobj in collection.data_objects:
            yield dobj

    print("Scanning files, may take several seconds...")

    while True:
        data_objects = list(walk_collection(collection))
        current_file = 0

        to_download = []

        # Scan collection files
        for data_obj in data_objects:
            target_path: pathlib.Path = arguments.output_dir / pathlib.Path(data_obj.path).relative_to(arguments.collection_path) 
            if not target_path.exists() or target_path.stat().st_size != data_obj.size:
                to_download.append((target_path, data_obj))

        # Download collection files
        total_files = len(to_download)
        for target_path, data_obj in to_download:
            if target_path.exists():
                target_path.unlink()

            # Ensure directory exists for the target file
            if not target_path.parent.is_dir():
                target_path.parent.mkdir(parents=True)

            # Download the file
            print(f"[{current_file+1}/{total_files}] Downloading file {str(target_path)}...", end='', flush=True)
            start = time.time()
            irods_session.data_objects.get(data_obj.path, str(target_path))
            duration_sec = time.time() - start
            size = sizeof_fmt(target_path.stat().st_size)
            print(f" done, {duration_sec:.2f} sec, {size}")
            current_file = current_file + 1

        print("Dataset downloaded, waiting for new files... If none expected, Ctrl+C to exit")    
        time.sleep(arguments.sleep_time)
