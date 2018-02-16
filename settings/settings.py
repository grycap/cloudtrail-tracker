AWS_REGION = 'us-east-1'
lambda_func_name = "alucloud230Query"
lambda_func_name_Uploads = "alucloud230Query"
stage_name = "QueryStage230"
table_name = "EventoCloudTrail_V3"
bucket_name = "alucloud230"
API_name = "prueba"
"""eventName 's that we DONT want to store - Filter"""
filterEventNames = ["get", "describe", "list", "info", "decrypt"]


index = 'userIdentity_userName-eventTime-index'
