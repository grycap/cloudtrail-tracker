AWS_REGION = 'us-east-1'
#Lambda function name for querying
lambda_func_name = "alucloud00-ctt-lambda-query"
#Lambda function name for automatic event uploads
lambda_func_name_trigger = "alucloud00-ctt-lambda-upload"
#Stage name for API Gateway
stage_name = "alucloud00-ctt-stage"
#DynamoDB Table name
table_name = "alucloud00-ctt-db"
#Preconfigured S3 bucket by CloudTrail
bucket_name = "alucloud00-ctt"
#API name
API_name = "alucloud00-ctt-api"
#eventNames that we DO NOT want to store - Filter
filterEventNames = ["assume","get", "describe", "list", "info", "decrypt", "checkmfa", "head"]
### Account IDs and permisiions
#aws_acct_id = "111111111111"
### Roles
#A role is needed with access to S3 / apig / lamba permissions
# arn_role = 'arn:aws:iam::111111111111:role/your-iam-role'
#Index name for DynamoDB Table - Do not modify if is not necessary
index = 'userIdentity_userName-eventTime-index'
