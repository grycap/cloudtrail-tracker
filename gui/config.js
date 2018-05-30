//all the provided keys are examples, go to Amazon Cognito and get yours

AWSCognito.config.region = 'eu-west-1'; //This is required to derive the endpoint

var poolData = {
    UserPoolId : 'us-east-1_31YsM4yXE', // your user pool id here
    ClientId : 'c7uisig4rr936sf6jqijglm36' // your client id here
};

var identityPoolId = 'eu-west-1:928sjpf-283osj3-293us3js-82372-730s'; //go to AWS Cognito Federated Identites

var userAttributes = ['email', 'phone_number']; //the standard attributes you require in AWS Cognito

var MFARequired = true; //do you require your clients to use MFA?