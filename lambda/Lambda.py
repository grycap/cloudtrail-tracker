
import boto3, os, sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import settings
import shutil


def create_lambda(name):
    client = boto3.client('lambda')

    zipName = "lambda"

    shutil.make_archive(zipName, 'zip', ".")


    response = client.create_function(
        FunctionName=name,
        Runtime='python3.6',
        Role='arn:aws:iam::974349055189:role/lambda-s3-apigw-role',
        Handler='getQuery.handler',
        Code={
            'ZipFile': open(zipName+'.zip', 'rb').read()
            # 'ZipFile': "fileb://" + file_get_contents(C:/Projects/src/zip/MyFunction.zip)
        },
        Description="Lambda function to query DynamoDB",
        Timeout=60,
        MemorySize=512,
    )


if (__name__ == '__main__'):
    print("Creating lambda . . . ",end='', flush=True)
    create_lambda("alucloud230Query")
    print("Done!")