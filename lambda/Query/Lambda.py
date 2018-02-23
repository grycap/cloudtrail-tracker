
import boto3, os, sys
os.system("rm -r DynamoDB/")
os.system("rm -r settings/")
sys.path.insert(1, os.path.join(sys.path[0], '../..'))
from settings import settings
import shutil

def update_dirs():

    os.system("cp -r ../../DynamoDB .")
    os.system("cp -r ../../settings .")

def create_lambda(name):
    client = boto3.client('lambda')

    zipName = "../lambda-querys"
    update_dirs()

    os.system("zip -r9 ../lambda-querys.zip *")
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
        Role=settings.arn_rol,
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
    create_lambda(settings.lambda_func_name)
    print("Done!")