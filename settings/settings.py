AWS_REGION = 'us-east-1'
lambda_func_name = "cloudtracking_querys"
lambda_func_name_trigger = "cloudtracking_upload_events_trigger"
stage_name = "cloudtrailtracker_stage"
table_name = "EventoCloudTrail_test1"
bucket_name = "alucloud230"
API_name = "cloudtrail_tracker"
"""eventName 's that we DONT want to store - Filter"""
filterEventNames = ["get", "describe", "list", "info", "decrypt"]


index = 'userIdentity_userName-eventTime-index'

### Account IDs and permisions
aws_acct_id = "974349055189"


### Roles
#Needed a rol with s3 / apig / lamba permissions
arn_rol = 'arn:aws:iam::974349055189:role/lambda-s3-apigw-role'