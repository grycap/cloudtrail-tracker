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
import boto3
import argparse, os, sys

from random import randint

sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from settings import settings
parser = argparse.ArgumentParser(description='Create a trigger when a file is uploaded to an specific S3 bucket.')
parser.add_argument('--bucket', type=str,
                   help='Bucket name.')
parser.add_argument('--lambda_name',type=str,
                   help='Lambda function name to launch on every event')

def create_trigger(name, bucket_name):
    client = boto3.client('lambda')
    #Getting info from lambda

    # arnLambda = response['FunctionArn']
    lambdaFunction = client.get_function(FunctionName=name)
    arnLambda = lambdaFunction["Configuration"]["FunctionArn"]

    #Adding trigger s3 -> lambda

    #need permisions before to add trigger
    response = client.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName=name,
        StatementId='ID-{}'.format(randint(0, 1000000)),
        Principal='s3.amazonaws.com',
        # SourceAccount='123456789012',
        # SourceArn='arn:aws:s3:::examplebucket/*'

    )

    s3 = boto3.resource('s3')
    bucket_notification = s3.BucketNotification(bucket_name)
    data = {}
    data['LambdaFunctionConfigurations'] = [
        {
            'Id': bucket_name + "_" + name,
            'LambdaFunctionArn': arnLambda,
            'Events': ["s3:ObjectCreated:*"],
            'Filter': {
                "Key": {
                    "FilterRules": [
                        {
                            "Name": "suffix",
                            "Value": "gz"
                        }

                    ]
                }
            }
        }
    ]

    bucket_notification.put(
        NotificationConfiguration=data
    )





if (__name__ == '__main__'):
    print("Creating trigger S3 -> Lambda . . . ",end='', flush=True)
    args = parser.parse_args()

    bucket_name = args.bucket
    lambda_name = args.lambda_name
    if not bucket_name:
        bucket_name = settings.bucket_name
    if not lambda_name:
        lambda_name = settings.lambda_func_name_trigger
    if not bucket_name or not lambda_name:
        print("\nLambda name or bucket name are not provided.")

    else:
        create_trigger(lambda_name, bucket_name)
        print("Done!")