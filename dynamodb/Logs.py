"""
Upload events.
"""

from __future__ import print_function
import os, argparse, sys, uuid, datetime, boto3, re, glob
import time

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
parser.add_argument("--f", help="Date from. YYYY-mm-dd date to finish the script", default='2007-01-01')
parser.add_argument("--bucket_name", help="Bucket name with stored events", default=None)

pattern = re.compile(".*_\d{8}([A-Z])\w+.json.gz")

def order_by_event(list_events):
    """
    Aux method for order a list of events.
    Remove not valid events

    :param list_events: list of strings [path/974349055189_CloudTrail_us-east-1_20170602T1040Z_i2yVtZoWqtLlq5oA.json.gz']
    :return: ordered list of tuple (date, string)
    """
    #split into string dates, covert to datetime
    dates = []
    events = []
    # dates = [datetime.datetime.strptime(e.split("_")[-2][:8], "%Y%m%d") for e in list_events]
    for e in list_events:
        try:
            dates.append(datetime.datetime.strptime(e.split("_")[-2][:8], "%Y%m%d"))
            events.append(e)
        except :
            """
            Not valid date
            """
            continue
    dates = list(zip(dates, events))
    dates.sort()
    return dates

def upload_events(path, table_name, to, from_):
    """Get all events from path, upload them and do a tracing.
    All tracing stored items is saved at path_tracing file.
    You can recall this functions without delete this file and start where you left"""
    to_finish = datetime.datetime.strptime(to, "%Y-%m-%d")
    from_start = datetime.datetime.strptime(from_, "%Y-%m-%d")
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

    #debug
    start_time = time.time()
    all_time = []
    #fin debug
    file_trace = open(path_tracing, "a+")
    for (e_date, e) in events:  # e = events file
        # debug
        start_event = time.time()
        if from_start > e_date:
            continue;
        if to_finish < e_date:
            break
        event = Event(e)
        db = UseDynamoDB("Uploading", verbose=False)

        db.store_event(table_name, event)
        file_trace.write(e+"\n")
        file_trace.flush()

        # debug
        elapsed_event = time.time() - start_time
        all_time.append(elapsed_event)
    # debug
    elapsed_time = time.time() - start_time
    print("Total time: %f" % elapsed_time)
    mean = sum(all_time) / len(all_time)
    print("mean time per event: %f" % mean)
    file_trace.close()
    os.remove(path_tracing)


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix
    res = []
    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                res.append( key)

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
    return res

def upload_events_from_bucket( bucket, to,from_, table_name, download_path="tmp/"):
    """
        Get all events from bucket and upload them .

    """
    to_finish = datetime.datetime.strptime(to, "%Y-%m-%d")
    from_start  = datetime.datetime.strptime(from_, "%Y-%m-%d")
    s3 = boto3.client('s3')
    # from_bucket = s3.list_objects_v2(Bucket=bucket)
    # list_ = from_bucket['Contents']
    list_ = get_matching_s3_keys(bucket)
    list_ = order_by_event(list_)

    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    for (e_date, s3_object) in list_:
        if from_start > e_date:
            continue;
        if to_finish < e_date:
            break
        name_obj = s3_object.split("/")[-1]
        # print(name_obj)
        e = download_path + name_obj
        s3.download_file(bucket, s3_object, e)
        print(e_date)
        event = Event(e)
        db = UseDynamoDB("Uploading", verbose=False)

        db.store_event(table_name, event)

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
    from_ = args.f
    bucket_name = args.bucket_name
    # bucket_name = "cursocloudaws-trail"
    if bucket_name:
        print("bucket_name {}".format(bucket_name))
        upload_events_from_bucket(bucket_name, to,from_, settings.table_name)
    else:
        print("path {}".format(path))
        upload_events(path, settings.table_name, to, from_)
    # print(settings.table_name)


if (__name__ == '__main__'):
    main()