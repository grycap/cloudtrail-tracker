import boto3

AWS_REGION = 'us-east-1'
lambda_func_name= "alucloud230Query"
REST_path = "{type}/{event}/{user}/{count}/{time1}/{time2}/{request}/{parameter}"
stage_name = "QueryStage230"
api_client = boto3.client('apigateway', region_name=AWS_REGION)
aws_lambda = boto3.client('lambda', region_name=AWS_REGION)

params_parameters = {

    "application/json": "{\n    "
                        "\"type\":  \"$input.params('type')\",\n    "
                        "\"event\": \"$input.params('event')\",\n    "
                        "\"user\":  \"$input.params('user')\", \n    "
                        "\"count\": \"$input.params('count')\",\n    "
                        "\"time1\": \"$input.params('time1')\",\n    "
                        "\"time2\": \"$input.params('time2')\",\n    "
                        "\"request\": \"$input.params('request')\",\n    "
                        "\"parameter\": \"$input.params('parameter')\"\n "
                        '}'

}

params_without = {

    "application/json": "{\n    "
                        "\"type\":  \"$input.params('type')\",\n    "
                        "\"event\": \"$input.params('event')\",\n    "
                        "\"user\":  \"$input.params('user')\", \n    "
                        "\"count\": \"$input.params('count')\",\n    "
                        "\"time1\": \"$input.params('time1')\",\n    "
                        "\"time2\": \"$input.params('time2')\"\n    "
                        '}'

}

def add_method(idAPI, parentIdResource, params = {}):
    print("Creating GET method")
    response = api_client.put_method(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        authorizationType='NONE',  # change in a future for COGNITO_USER_POOLS
    )

    lambda_version = aws_lambda.meta.service_model.api_version

    uri_data = {
        "aws-region": AWS_REGION,
        "api-version": lambda_version,
        "aws-acct-id": "974349055189",
        "lambda-function-name": lambda_func_name,
        "lambda-function-name-path": lambda_func_name + "/{type}/{event}/{user}/{count}/{time1}/{time2}/",
    }
    # arn:aws:lambda:us-east-1:974349055189:function:alucloud230Query
    uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(
        **uri_data)
    print("Updating integration")
    response = api_client.put_integration(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        # type='HTTP' | 'AWS' | 'MOCK' | 'HTTP_PROXY' | 'AWS_PROXY',
        type='AWS',
        # timeoutInMillis=29000,
        integrationHttpMethod='POST',
        uri=uri,
        requestTemplates=params,
        passthroughBehavior='WHEN_NO_TEMPLATES',
        # cacheNamespace='string',
        # cacheKeyParameters=[
        #     'string',
        # ],
        # contentHandling='CONVERT_TO_BINARY' | 'CONVERT_TO_TEXT',

    )

    print("Creating integration response")
    ## create GET method response
    api_client.put_method_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        statusCode="200",
        responseParameters={
            'method.response.header.Access-Control-Allow-Origin': False
        },
        responseModels={
            'application/json': 'Empty'
        }
    )

    response = api_client.put_integration_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='GET',
        statusCode='200',
        selectionPattern=".*",
        responseParameters={
            'method.response.header.Access-Control-Allow-Origin': '\'*\''
        },
        responseTemplates={
            'application/json': ''
        }
    )

    # Add an options method to the rest api
    api_method = api_client.put_method(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='OPTIONS',
        authorizationType='NONE'
    )
    # Set the put integration of the OPTIONS method
    api_client.put_integration(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={
            'application/json': '{"statusCode": 200}'
        }
    )

    # Set the put method response of the OPTIONS method
    api_client.put_method_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': False,
            'method.response.header.Access-Control-Allow-Origin': False,
            'method.response.header.Access-Control-Allow-Methods': False
        },
        responseModels={
            'application/json': 'Empty'
        }
    )

    # Set the put integration response of the OPTIONS method
    api_client.put_integration_response(
        restApiId=idAPI,
        resourceId=parentIdResource,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': '\'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token\'',
            'method.response.header.Access-Control-Allow-Methods': '\'GET,OPTIONS\'',
            'method.response.header.Access-Control-Allow-Origin': '\'*\''
        },
        responseTemplates={
            'application/json': ''
        }
    )

def create_API(name):

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
        pathPart=lambda_func_name,

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
        if pathPart == "{time2}":
            add_method(idAPI, parentIdResource, params_without)

    add_method(idAPI, parentIdResource, params_parameters)

    print("Adding permisions lambda -> APIGateway")
    ## Add permisions from lambda to api gateway
    # uri_data['aws-api-id'] = idAPI
    # source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/POST/{lambda-function-name}".format(
    #     **uri_data)

    aws_lambda.add_permission(
        FunctionName=lambda_func_name,
        StatementId=idAPI+"API_gatewat",
        Action="lambda:InvokeFunction",
        Principal="apigateway.amazonaws.com",
        # SourceArn=source_arn
    )

    print("Creating stage")
    stage = api_client.create_deployment(
        restApiId=idAPI,
        stageName=stage_name,
    )


    # URL stage : https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}/{RESOURCE}


    print("URL: https://{}.execute-api.{}.amazonaws.com/{}/{}/".format(idAPI, AWS_REGION, stage_name, lambda_func_name))




if (__name__ == '__main__'):
    print("Creating API Rest . . . ",end='', flush=True)

    create_API("prueba")

    print("Done!")