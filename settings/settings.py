AWS_REGION = 'us-east-1'
#Lambda function name for querying
lambda_func_name = "cloudtrailTrackerQueries"
#Lambda function name for automatic event upload
lambda_func_name_trigger = "cloudtrailTrackerUpload"
#Stage name for API Gateway
stage_name = "cloudtrailtrackerStage"
#DynamoDB Table name
table_name = "cloudtrailtrackerdb"
#Preconfigured S3 bucket by CloudTrail
bucket_name = "cursocloudaws-trail"
#API name
API_name = "cloudtrailTrackerAPI"
#eventNames that we DO NOT want to store - Filter
filterEventNames = ["get", "describe", "list", "info", "decrypt", "checkmfa", "head", "assumerole"]
#Index name for DynamoDB Table - Dont modify if is not necessary
index = 'userIdentity_userName-eventTime-index'

