import boto3


#Function for starting athena query
def run_query(query, database, s3_output):
    client = boto3.client('athena')
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
            },
        ResultConfiguration={
            'OutputLocation': s3_output,
            }
        )
    print('Execution ID: ' + response['QueryExecutionId'])
    return response

def main():
    database = 'test_database'
    # table = 'persons'
    create_database = "CREATE DATABASE IF NOT EXISTS %s;" % (database)
    create_table = \
        """CREATE EXTERNAL TABLE IF NOT EXISTS my_cloudtrail_table (
   eventversion STRING,
   userIdentity STRUCT<
      type:STRING,
      principalid:STRING,
      arn:STRING,
      accountid:STRING,
      invokedby:STRING,
      accesskeyid:STRING,
      userName:String,
      sessioncontext:STRUCT<
         attributes:STRUCT<
            mfaauthenticated:STRING,
            creationdate:STRING>,
         sessionIssuer:STRUCT<
            type:STRING,
            principalId:STRING,
            arn:STRING,
            accountId:STRING,
            userName:STRING>>>,
   eventTime STRING,
   eventSource STRING,
   eventName STRING,
   awsRegion STRING,
   sourceIpAddress STRING,
   userAgent STRING,
   errorCode STRING,
   errorMessage STRING,
   requestId STRING,
   eventId STRING,
   resources ARRAY<STRUCT<
      ARN:STRING,
      accountId:STRING,
      type:STRING>>,
   eventType STRING,
   apiVersion STRING,
   readOnly BOOLEAN,
   recipientAccountId STRING,
   sharedEventID STRING,
   vpcEndpointId STRING
 )
 ROW FORMAT SERDE 'com.amazon.emr.hive.serde.CloudTrailSerde'
 STORED AS INPUTFORMAT 'com.amazon.emr.cloudtrail.CloudTrailInputFormat'
 OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
 LOCATION 's3://alucloud230/';"""

    # Execute all queries
    query_1 = "SELECT useridentity.username, sourceipaddress, eventtime, additionaleventdata FROM default.my_cloudtrail_table WHERE eventname = 'ConsoleLogin'";
    s3_ouput = 'string'
    queries = [create_database, create_table, query_1]
    for q in queries:
        print("Executing query: %s" % (q))
        res = run_query(q, database, s3_ouput)

        print(res)


if (__name__ == '__main__'):
    main()