import boto3

AWS_REGION = 'us-east-1'
lambda_func_name= "alucloud230Query"
REST_path = "{type}/{event}/{user}/{count}/{time1}/{time2}"

def create_API(name):
    api_client = boto3.client('apigateway', region_name=AWS_REGION)
    aws_lambda = boto3.client('lambda', region_name=AWS_REGION)
    response = api_client.create_rest_api(
        name=name,
        description='Api REST 230',
        version='0.1',
    )

    idAPI = response['id']
    print("API id: {}".format(idAPI))
    responseResource = api_client.get_resources(
        restApiId=idAPI,
        # position='string',
        # limit=123,
        # embed=[
        #     'string',
        # ]
    )
    print("API resources {}".format(responseResource))
    #only have one resource
    idResource = responseResource['items'][0]['id']
    path = responseResource['items'][0]['path']
    print("API resources - PATH {}".format(path))
    print("API creating resource /{}".format(lambda_func_name))
    ## create resource /lambda_func_name
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=idResource,  # resource id for the Base API path
        pathPart=lambda_func_name
    )


    parentIdResource = responseResource['id']
    parentPath = responseResource['path']

    pathParts = REST_path.split("/")
    for pathPart in pathParts:
        print("Creating path {}".format(pathPart))
        ## create resource /lambda_func_name/{type}
        responseResource = api_client.create_resource(
            restApiId=idAPI,
            parentId=parentIdResource,  # resource id for the Base API path
            pathPart=pathPart
        )
        parentIdResource = responseResource['id']

    print("Creating GET method")
    response = api_client.put_method(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        authorizationType='NONE', # change in a future for COGNITO_USER_POOLS
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
    print("Updating integration")
    response = api_client.put_integration(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        # type='HTTP' | 'AWS' | 'MOCK' | 'HTTP_PROXY' | 'AWS_PROXY',
        type='AWS',
        integrationHttpMethod='GET',
        uri=uri,
        # requestParameters={
        #     'string': 'string'
        # },
        # requestTemplates={
        #     'string': 'string'
        # },
        # passthroughBehavior='string',
        # cacheNamespace='string',
        # cacheKeyParameters=[
        #     'string',
        # ],
        # contentHandling='CONVERT_TO_BINARY' | 'CONVERT_TO_TEXT',
        # timeoutInMillis=29000
    )

    print("Creating integration response")
    response = api_client.put_integration_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        statusCode='200',
        selectionPattern=".*"
        # responseParameters={
        #     'string': 'string'
        # },
        # responseTemplates={
        #     'string': 'string'
        # },
        # contentHandling='CONVERT_TO_BINARY' | 'CONVERT_TO_TEXT'
    )
    ## create POST method response
    api_client.put_method_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        statusCode="200",
    )



if (__name__ == '__main__'):
    print("Creating API Rest . . . ",end='', flush=True)

    create_API("prueba")

    print("Done!")