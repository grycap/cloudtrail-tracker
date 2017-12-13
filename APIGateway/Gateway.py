import boto3

AWS_REGION = 'us-east-1'
lambda_func_name= "alucloud230Query"

def create_API(name):
    api_client = boto3.client('apigateway', region_name=AWS_REGION)
    aws_lambda = boto3.client('lambda', region_name=AWS_REGION)
    response = api_client.create_rest_api(
        name=name,
        description='Api REST 230',
        version='0.1',
    )

    idAPI = response['id']

    responseResource = api_client.get_resources(
        restApiId=idAPI,
        # position='string',
        # limit=123,
        # embed=[
        #     'string',
        # ]
    )

    #only have one resource
    idResource = responseResource['items'][0]['id']
    path = responseResource['items'][0]['path']

    ## create resource
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=path,  # resource id for the Base API path
        pathPart=lambda_func_name
    )

    # only have one resource
    idResource = responseResource['id']

    ## create POST method
    responseMethod = api_client.put_method(
        restApiId=idAPI,
        resourceId=idResource,
        httpMethod='POST',
        authorizationType='NONE',
        apiKeyRequired=False,
    )

    lambda_version = aws_lambda.meta.service_model.api_version

    uri_data = {
        "aws-region": AWS_REGION,
        "api-version": lambda_version,
        "aws-acct-id": "974349055189",
        "lambda-function-name": lambda_func_name,
    }

    uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(
        **uri_data)

    ## create integration
    integration_resp = api_client.put_integration(
        restApiId=idAPI,
        resourceId=idResource,
        httpMethod="POST",
        type="AWS",
        integrationHttpMethod="POST",
        uri=uri,
    )

    api_client.put_integration_response(
        restApiId=idAPI,
        resourceId=idResource,
        httpMethod="POST",
        statusCode="200",
        selectionPattern=".*"
    )

    ## create POST method response
    api_client.put_method_response(
        restApiId=idAPI,
        resourceId=idResource,
        httpMethod="POST",
        statusCode="200",
    )



if (__name__ == '__main__'):
    print("Creating API Rest . . . ",end='', flush=True)

    create_API("prueba230")

    print("Done!")