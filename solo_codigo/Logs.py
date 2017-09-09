from __future__ import print_function
import boto
from to_dynamo import UseDynamoDB
from my_parser import Event
import os
from __future__ import print_function
import boto
import os
import sys
import uuid


def guardar_eventos():

    table_name = 'EventoCloudTrail_230'
    conn = boto.connect_s3()
    
    bucket = conn.get_bucket('alucloud230')
    LOCAL_PATH = "./examples/"
    for l in bucket.list():
        print(l.name.encode('utf-8'))
        keyString = str(l.key)
        
        # check if file exists locally, if not: download it
        
        if not os.path.exists(LOCAL_PATH + keyString):
            file_path = LOCAL_PATH + keyString
            print("\nGuardando evento %s " % file_path)
            l.get_contents_to_filename(file_path)
            
            event = Event(file_path)
            db = UseDynamoDB("prueba")
            db.guardar_evento(table_name,event)


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
    
    print("Downloading log in bucket {} with key {}".format(bucket, key))
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    print("bucket %s , key %s , download_path %s" % (bucket, key, download_path))
    # s3_client.download_file(bucket, key, download_path)
    #
    # grayify_image(download_path)
    # bucket_out = bucket + '-out'
    # print("Uploading image in bucket {} with key {}".format(bucket_out, key))
    # s3_client.upload_file(download_path, '{}'.format(bucket_out), key)
    #
    # print("Changing ACLs for public-read for object in bucket {} with key{}".format(bucket_out,key))
    # s3_resource = boto3.resource('s3')
    # obj = s3_resource.Object(bucket_out, key)
    # obj.Acl().put(ACL='public-read')
    # if __name__ == '__main__':
    #     grayify_image(sys.argv[1])


def main():
    guardar_eventos()


if (__name__ == '__main__'):
    main()