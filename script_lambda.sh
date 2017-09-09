aws lambda create-function \
--region us-east-1 \
--function-name lambda-logs-$ID \
--zip-file fileb://$HOME/lambda-logs-$ID.zip \
--role arn:aws:iam::974349055189:role/lambda-s3-execution-role \
--handler Logs.handler \
--runtime python2.7 \
--timeout 10 \
--memory-size 128
