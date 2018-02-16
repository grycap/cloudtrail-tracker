import boto3, os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
try:
    from settings import settings
except:
    from .settings import settings

api_client = boto3.client('apigateway', region_name=settings.AWS_REGION)
aws_lambda = boto3.client('lambda', region_name=settings.AWS_REGION)



params = {
    "application/json": "{\n    "
                        "\"type\":  \"$input.params('type')\",\n    "
                        "\"event\": \"$input.params('event')\",\n    "
                        "\"user\":  \"$input.params('user')\", \n    "
                        "\"time1\": \"$input.params('time1')\",\n    "
                        "\"time2\": \"$input.params('time2')\"\n    "
                        '}'

}

def add_method(idAPI, parentIdResource, params = {}, queryString={}):
    print("Creating GET method")

    if queryString:
        response = api_client.put_method(
            restApiId=idAPI,
            resourceId=parentIdResource,
            httpMethod='GET',
            authorizationType='NONE',  # change in a future for COGNITO_USER_POOLS
            requestParameters=queryString,
        )
    else:
        response = api_client.put_method(
            restApiId=idAPI,
            resourceId=parentIdResource,
            httpMethod='GET',
            authorizationType='NONE',  # change in a future for COGNITO_USER_POOLS
        )

    lambda_version = aws_lambda.meta.service_model.api_version

    uri_data = {
        "aws-region": settings.AWS_REGION,
        "api-version": lambda_version,
        "aws-acct-id": "974349055189",
        "lambda-function-name": settings.lambda_func_name,
        # "lambda-function-name-path": lambda_func_name + "/{type}/{event}/{user}/{count}/{time1}/{time2}/",
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
    print("API creating resource /{}".format(settings.lambda_func_name))
    ## create resource /lambda_func_name
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=idResource,  # resource id for the Base API path
        pathPart=settings.lambda_func_name,

    )


    parentIdResource = responseResource['id']
    parentPath = responseResource['path']



    ######/users
    users = "users"
    print("Creating path {}".format(users))
    ## create resource /lambda_func_name/{type}
    responseResource = api_client.create_resource(
            restApiId=idAPI,
            parentId=parentIdResource,  # resource id for the Base API path
            pathPart=users
    )
    parentIdResourceUsers = responseResource['id']
    params = {
        "application/json": "{\n    "
                            "\"list_users\":  \"list_users\"\n    "
                            '}'

    }

    add_method(idAPI, parentIdResourceUsers, params)
    ###### end /users

    ##### /users/{user}
    print("Creating path {}".format(users+"/{users}"))
    ## create resource /lambda_func_name/{type}
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=parentIdResourceUsers,  # resource id for the Base API path
        pathPart="{user}"
    )
    parentIdResourceUsersUser = responseResource['id']
    params = {
        "application/json": "{\n    "
                            "\"user\":  \"$input.params('user')\",\n    "
                            "\"count\":  \"$input.params('count')\",\n    "
                            "\"eventName\":  \"$input.params('eventName')\",\n    "
                            "\"from\":  \"$input.params('from')\",\n    "
                            "\"to\":  \"$input.params('to')\",\n    "
                            "\"param\":  \"$input.params('param')\",\n    "
                            "\"value\":  \"$input.params('value')\"\n    "
                            '}'

    }
    queryString = {
        'method.request.querystring.count': False,
        'method.request.querystring.eventName': False,
        'method.request.querystring.from': False,
        'method.request.querystring.to': False,
        'method.request.querystring.param': False,
        'method.request.querystring.value': False,
    }

    add_method(idAPI, parentIdResourceUsersUser, params, queryString=queryString)
    ##### end /users/{user}

    ##### /services
    services = "services"
    print("Creating path {}".format(services))
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=parentIdResource,  # resource id for the Base API path
        pathPart=services
    )
    parentIdResourceServices = responseResource['id']

    print("Creating path {}".format(services+"/{service}"))
    responseResource = api_client.create_resource(
        restApiId=idAPI,
        parentId=parentIdResourceServices,  # resource id for the Base API path
        pathPart="{service}"
    )
    parentIdResourceServicesService = responseResource['id']

    params = {
        "application/json": "{\n    "
                            "\"service\":  \"$input.params('service')\",\n    "
                            "\"count\":  \"$input.params('count')\",\n    "
                            "\"eventName\":  \"$input.params('eventName')\",\n    "
                            "\"from\":  \"$input.params('from')\",\n    "
                            "\"to\":  \"$input.params('to')\",\n    "
                            "\"param\":  \"$input.params('param')\",\n    "
                            "\"value\":  \"$input.params('value')\"\n    "
                            '}'

    }
    queryString = {
        'method.request.querystring.count': False,
        'method.request.querystring.eventName': False,
        'method.request.querystring.from': False,
        'method.request.querystring.to': False,
        'method.request.querystring.param': False,
        'method.request.querystring.value': False,
    }

    add_method(idAPI, parentIdResourceServicesService, params, queryString=queryString)

    print("Adding permisions lambda -> APIGateway")
    ## Add permisions from lambda to api gateway
    # uri_data['aws-api-id'] = idAPI
    # source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/POST/{lambda-function-name}".format(
    #     **uri_data)

    aws_lambda.add_permission(
        FunctionName=settings.lambda_func_name,
        StatementId=idAPI+"API_gatewat",
        Action="lambda:InvokeFunction",
        Principal="apigateway.amazonaws.com",
        # SourceArn=source_arn
    )

    print("Creating stage")
    stage = api_client.create_deployment(
        restApiId=idAPI,
        stageName=settings.stage_name,
    )


    # URL stage : https://{API_ID}.execute-api.{REGION}.amazonaws.com/{STAGE}/{RESOURCE}


    print("URL: https://{}.execute-api.{}.amazonaws.com/{}/{}/".format(idAPI, settings.AWS_REGION, settings.stage_name, settings.lambda_func_name))




if (__name__ == '__main__'):
    print("Creating API Rest . . . ",end='', flush=True)

    create_API(settings.API_name)

    print("Done!")