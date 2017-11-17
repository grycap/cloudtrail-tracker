from __future__ import print_function
from to_dynamo import UseDynamoDB
from my_parser import Event
import os
import boto3
import uuid
import botocore


def guardar_eventos():

    bucket_name = 'alucloud230'

    table_name = 'EventoCloudTrail_2302'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    #bucket = conn.get_bucket('alucloud230')
    LOCAL_PATH = "./examples/"
    for l in bucket.objects.all():
        
        keyString = str(l.key)
        print(LOCAL_PATH + keyString)
        # check if file exists locally, if not: download it
        
        if not os.path.exists(LOCAL_PATH + keyString):
            file_path = LOCAL_PATH + keyString
            print("\nGuardando evento %s " % file_path)
            #l.get_contents_to_filename(file_path)
            try:
                s3.Bucket(bucket_name).download_file(keyString, LOCAL_PATH + keyString)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
            
            event = Event(file_path)
            db = UseDynamoDB("prueba")
            db.guardar_evento(table_name,event)
            os.remove(LOCAL_PATH + keyString)


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    
    print("Downloading log in bucket {} with key {}".format(bucket, key))
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    print("bucket %s , key %s , download_path %s" % (bucket, key, download_path))


def main():
    guardar_eventos()


if (__name__ == '__main__'):
    main()