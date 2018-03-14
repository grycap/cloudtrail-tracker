import boto3
import argparse

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
        StatementId='ID-0',
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
    if not bucket_name or not lambda_name:
        print("\nLambda name or bucket name are not provided.")

    else:
        create_trigger(lambda_name, bucket_name)
        print("Done!")