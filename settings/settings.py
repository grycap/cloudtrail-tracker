AWS_REGION = 'us-east-1'
#Lambda function name for querying
lambda_func_name = "cloudtrailTracker-query_v2"
#Lambda function name for automatic event upload
lambda_func_name_trigger = "cloudtrailTracker-Upload_v2"
#Stage name for API Gateway
stage_name = "dev"
#DynamoDB Table name
table_name = "cloudtrailtrackerdb_v2"
#Preconfigured S3 bucket by CloudTrail
bucket_name = "cursocloudaws-trail"
#eventNames that we DO NOT want to store - Filter
filterEventNames = ["get", "describe", "list", "info", "decrypt", "checkmfa", "head", "assumerole", "consolelogin"]
#Index name for DynamoDB Table - Dont modify if is not necessary
index = 'userIdentity_userName-eventTime-index'

