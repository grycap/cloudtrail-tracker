AWS_REGION = 'us-east-1'
#Lambda function name for querying
lambda_func_name = "lambda-ctt-00-query"
#Lambda function name for automatic event uploads
lambda_func_name_trigger = "lambda-ctt-00-upload"
#Stage name for API Gateway
stage_name = "stage-ctt-00"
#DynamoDB Table name
table_name = "db-alucloud00-ctt"
#Preconfigured S3 bucket by CloudTrail
bucket_name = "alucloud00"
#API name
API_name = "CloudtrailTrackerAPI00"
#eventNames that we DO NOT want to store - Filter
filterEventNames = ["assume","get", "describe", "list", "info", "decrypt", "checkmfa", "head"]
### Account IDs and permisiions
#aws_acct_id = "111111111111"
### Roles
#A role is needed with access to S3 / apig / lamba permissions
# arn_role = 'arn:aws:iam::111111111111:role/your-iam-role'
#Index name for DynamoDB Table - Do not modify if is not necessary
index = 'userIdentity_userName-eventTime-index'
