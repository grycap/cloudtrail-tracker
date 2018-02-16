
import boto3, os, sys

sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from settings import settings

import shutil


def create_lambda(name):
    client = boto3.client('lambda')

    zipName = "../lambda-uploads"
    os.system("rm -r DynamoDB/")
    os.system("rm -r settings/")
    os.system("cp -r ../../DynamoDB .")
    os.system("cp -r ../../settings .")
    os.system("zip -r9 ../lambda-uploads.zip *")
    shutil.make_archive(zipName, 'zip', ".")

    try:
        client.delete_function(
            FunctionName=name,
        )
    except:
        pass

    response = client.create_function(
        FunctionName=name,
        Runtime='python3.6',
        Role='arn:aws:iam::974349055189:role/lambda-s3-apigw-role',
        Handler='Upload.handler',
        Code={
            'ZipFile': open(zipName+'.zip', 'rb').read()
            # 'ZipFile': "fileb://" + file_get_contents(C:/Projects/src/zip/MyFunction.zip)
        },
        Description="Lambda function to query DynamoDB",
        Timeout=60,
        MemorySize=512,
    )
    # arnLambda = response['FunctionArn']
    # s3 = boto3.resource('s3')
    # bucket_notification = s3.BucketNotification(settings.bucket_name)
    # data = {}
    # data['LambdaFunctionConfigurations'] = [
    #     {
    #         'Id':settings.bucket_name + "_"  + name ,
    #         'LambdaFunctionArn': arnLambda,
    #         'Events': ["s3:ObjectCreated:*"]
    #     }
    # ]
    #
    # response = client.add_permission(
    #     Action='lambda:InvokeFunction',
    #     FunctionName=name,
    #     StatementId='ID-1',
    #     Principal='s3.amazonaws.com',
    #     # SourceAccount='123456789012',
    #     # SourceArn='arn:aws:s3:::examplebucket/*'
    #
    # )
    #
    # bucket_notification.put(
    #     NotificationConfiguration=data
    # )
    #




if (__name__ == '__main__'):
    print("Creating lambda . . . ",end='', flush=True)
    create_lambda("alucloud230UploadEvents")
    print("Done!")