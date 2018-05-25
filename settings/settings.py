AWS_REGION = 'us-east-1'
#Lambda function name for querying
lambda_func_name = "cloudtracking_querys"
#Lambda function name for automatic event upload
lambda_func_name_trigger = "cloudtrail-tracker-uploads"
#Stage name for API Gateway
stage_name = "cloudtrailtracker_stage"
#DynamoDB Table name
table_name = "EventoCloudTrail"
#Preconfigured S3 bucket by CloudTrail
bucket_name = "cursocloudaws-trail"
#API name
API_name = "cloudtrail_tracker"
#eventName 's that we DONT want to store - Filter
filterEventNames = ["get", "describe", "list", "info", "decrypt", "checkmfa", "head"]
### Account IDs and permisions
aws_acct_id = "974349055189"
### Roles
#Needed a rol with s3 / apig / lamba permissions
arn_rol = 'arn:aws:iam::974349055189:role/lambda-s3-apigw-role'
#Index name for DynamoDB Table - Dont modify if is not necessary
index = 'userIdentity_userName-eventTime-index'
