# CloudTrail-Tracker
# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
import boto3
import os
import sys
import uuid

from settings import settings
from dynamodb import Logs

s3_client = boto3.client('s3')

def handler(event, context):

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        print("Downloading event in bucket {} with key {}".format(bucket, key))
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        s3_client.download_file(bucket, key, download_path)
        print("Uploading event ...")
        # bucket_out = bucket + '-out'
        # s3_client.upload_file(download_path, '{}'.format(bucket_out), key)
        Logs.upload_event_handler(download_path, settings.table_name)
        print("Finished")

if __name__ == '__main__':
    print(settings.table_name)
    handler({},None)