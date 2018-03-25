"""
Upload events.
"""

from __future__ import print_function
import os, argparse, sys, uuid, datetime, boto3, re, glob

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
from dynamodb.Write import UseDynamoDB
from dynamodb.my_parser import Event
from dynamodb.analysis import get_structure

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import settings

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="Path that contains items to start to upload", default='./examples')
parser.add_argument("--t", help="Date to. YYYY-mm-dd date to finish the script", default='2030-01-20')
parser.add_argument("--bucket_name", help="Bucket name with stored events", default=None)

pattern = re.compile(".*_\d{8}([A-Z])\w+.json.gz")

def order_by_event(list_events):
    """
    Aux method for order a list of events

    :param list_events: list of strings [path/974349055189_CloudTrail_us-east-1_20170602T1040Z_i2yVtZoWqtLlq5oA.json.gz']
    :return: ordered list of tuple (date, string)
    """
    #split into string dates, covert to datetime
    dates = [datetime.datetime.strptime(e.split("_")[-2][:8], "%Y%m%d") for e in list_events]
    dates = list(zip(dates, list_events))
    dates.sort()
    return dates

def upload_events(path, table_name, to):
    """Get all events from path, upload them and do a tracing.
    All tracing stored items is saved at path_tracing file.
    You can recall this functions without delete this file and start where you left"""
    to_finish = datetime.datetime.strptime(to, "%Y-%m-%d")
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

    events = order_by_event(events)


    file_trace = open(path_tracing, "a+")
    for (e_date, e) in events:  # e = events file
        if to_finish < e_date:
            break
        print(e_date, e)
        event = Event(e)
        db = UseDynamoDB("Uploading", verbose=False)

        db.store_event(table_name, event)
        file_trace.write(e+"\n")
        file_trace.flush()


    file_trace.close()
    os.remove(path_tracing)

def upload_events_from_bucket(bucket_name, table_name, to):
    """
    Get all events from bucket and upload them .

    """
    pass
def download_dir( bucket, to, table_name, download_path="tmp/"):
    to_finish = datetime.datetime.strptime(to, "%Y-%m-%d")
    s3 = boto3.client('s3')
    list_ = s3.list_objects(Bucket=bucket)['Contents']
    list_ = [l['Key'] for l in list_ if pattern.match(l['Key'])]
    list_ = order_by_event(list_)
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    for (e_date, s3_object) in list_:
        if to_finish < e_date:
            break
        print(s3_object)
        #datetime.datetime.strptime(e.split("_")[-2][:8], "%Y%m%d")

        s3.download_file(bucket, s3_object, download_path + s3_object)
        upload_events(download_path, table_name, to)

        #delet content dir
        files = glob.glob(download_path+"*")
        for f in files:
            os.remove(f)


def upload_event_handler(path, table_name):
    """Upload without tracing.
    Util for lambda function
    Now path is one file"""
    # events = get_structure(path)
    event = Event(path)
    db = UseDynamoDB("Uploading", verbose=False)
    db.store_event(table_name, event)




def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

    print("Downloading log in bucket {} with key {}".format(bucket, key))
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    print("bucket %s , key %s , download_path %s" % (bucket, key, download_path))


def main():
    args = parser.parse_args()
    path = args.path
    to = args.t
    bucket_name = args.bucket_name
    if bucket_name:

        # upload_events_from_bucket(bucket_name, settings.table_name, to)
        download_dir(bucket_name, to, settings.table_name)
    else:
        upload_events(path, settings.table_name, to)
    # print(settings.table_name)


if (__name__ == '__main__'):
    main()