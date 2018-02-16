from __future__ import print_function
try:
    from Write import UseDynamoDB
    from my_parser import Event
    from analysis import get_structure
except:
    from .Write import UseDynamoDB
    from .my_parser import Event
    from .analysis import get_structure
import os, argparse
import uuid
import sys
from settings import settings

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="Path that contains items to start the analysis", default='./examples')


def upload_events(path, table_name = 'EventoCloudTrail_V3'):
    # Get all events from path
    path_tracing  = "tracing_items"
    print("Path of files: %s with " % (path))

    if not os.path.exists(os.path.join(path_tracing)):
        f = open(path_tracing, "w")
        f.close()

    file_trace = open(path_tracing, "r")

    traced_items = file_trace.readlines()
    traced_items = [x[:-1] for x in traced_items]
    file_trace.close()
    print("Traced files: %d" % (len(traced_items)))
    events = get_structure(path)

    print("Number of files: %d" % len(events))
    events = list(set(events) - set(traced_items))
    print("Number of total files to upload: %d" % len(events))

    file_trace = open(path_tracing, "a+")
    for e in events:  # e = events file
        event = Event(e)
        db = UseDynamoDB("Uploading", verbose=False)

        db.guardar_evento(table_name, event)
        file_trace.write(e+"\n")
        file_trace.flush()


    file_trace.close()

def upload_event_handler(path, table_name):
    """Upload without tracing.
    Util for lambda function
    Now path is one file"""
    # events = get_structure(path)
    event = Event(path)
    db = UseDynamoDB("Uploading", verbose=True)
    db.guardar_evento(table_name, event)




def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    
    print("Downloading log in bucket {} with key {}".format(bucket, key))
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    print("bucket %s , key %s , download_path %s" % (bucket, key, download_path))


def main():
    # args = parser.parse_args()
    # path = args.path
    # upload_events(path, settings.table_name)
    print(settings.table_name)


if (__name__ == '__main__'):
    main()