import boto3, os, sys

def create_trigger(name, bucket_name):
    client = boto3.client('lambda')

    {'ResponseMetadata': {'RequestId': 'ac1e4f3b-26df-11e8-a70c-195bef096ee4', 'HTTPStatusCode': 200,
                          'HTTPHeaders': {'date': 'Tue, 13 Mar 2018 16:57:54 GMT', 'content-type': 'application/json',
                                          'content-length': '1892', 'connection': 'keep-alive',
                                          'x-amzn-requestid': 'ac1e4f3b-26df-11e8-a70c-195bef096ee4'},
                          'RetryAttempts': 0}, 'Configuration': {'FunctionName': 'cloudtrail-tracker-uploader',
                                                                 'FunctionArn': 'arn:aws:lambda:us-east-1:974349055189:function:cloudtrail-tracker-uploader',
                                                                 'Runtime': 'python3.6',
                                                                 'Role': 'arn:aws:iam::974349055189:role/lambda-s3-apigw-role',
                                                                 'Handler': 'lambda/eventuploads/Upload.handler',
                                                                 'CodeSize': 428089,
                                                                 'Description': 'CloudTrail-Tracker (Event Uploads)',
                                                                 'Timeout': 30, 'MemorySize': 128,
                                                                 'LastModified': '2018-03-13T16:48:23.695+0000',
                                                                 'CodeSha256': 'ux1hKak85yrvuWIn1lGiFRa1kZvTTOGrH2II87/ILtA=',
                                                                 'Version': '$LATEST',
                                                                 'TracingConfig': {'Mode': 'PassThrough'},
                                                                 'RevisionId': 'c9f1ea68-503c-443e-84af-ee1d22ec69a7'},
     'Code': {'RepositoryType': 'S3',
              'Location': 'https://prod-04-2014-tasks.s3.amazonaws.com/snapshots/974349055189/cloudtrail-tracker-uploader-87e63ba1-716e-45a7-bcd1-1ac94b606823?versionId=KMsBqCITh2F20rHPrpHaDmXDne0ziwl4&X-Amz-Security-Token=FQoDYXdzEDIaDFogQwXZQ3ra1iCWFSK3A%2B7FV51HItCG07PGS8kZUR9U1wZkiYVrkNkMuiHXYyYIGZ3UXZkXK524p9imcc0yWXiQaZHEFbe%2BDYttYBtTkVndfDQt1aRwMbHr5M6AfDFor3yfdwysV89jSQtzWNpXGZoFuH%2FP3w6BNbzwo2KilQ1WccoXslLnMlqbzgCjA3IFDAej0ZCKO1WJrREEIFrgkikFTj%2FJ1m8lRW3twhhoMuUMHFKWcxkLMdL%2BPXHUOLx0naaac3HjvKHvNzBoiUaGlZ76nKc5LVAlnHJYUUfYbVyCOTmY0IFvyj0jnSb6PEJ41dSCBg800mOxCfzA1rbDpWg1FmfG6cq9rmTe5SvtY0eNqetEG5zg8VYMIeIQOQMWPRPR70lQx4gUHxZ7P%2BywLwtq4MlC0fjMXUxtn2KSzlEIoot8TgwPCCjYhlk9gEDLhDmER90fE34o1%2BFIMX9R1AW3JI1u1sk9sFGPUhpxuDqf6DsAsBx4rBJrtxWlkGzURaPayybGd68mmoXvwKW70eSXYChBH4rNgbghP3R8YTv2li%2BgFwT90yJWEmfbq1NyXIr0i%2Fde1kzn44TSPgdG8JNzxihm8SYo4vaf1QU%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20180313T165754Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIAIVLV4PR6CVSOV5OQ%2F20180313%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=8a857ffa7e7613c1d0601e8181375ac9f4b76d67262e5e011318ba6ac390b7f7'},
     'Tags': {'STAGE': 'dev'}}

    #Getting info from lambda

    # arnLambda = response['FunctionArn']
    lambdaFunction = client.get_function(FunctionName=name)
    print(lambdaFunction)
    print(lambdaFunction.get("lambdaFunction"))
    print(lambdaFunction["Configuration"]["FunctionArn"])
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