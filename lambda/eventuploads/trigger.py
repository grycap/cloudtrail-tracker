import boto3, os, sys

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
    bucket_name = "alucloud230"
    create_trigger("cloudtrail-tracker-uploader", bucket_name)
    print("Done!")