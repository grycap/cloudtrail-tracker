import boto3, time
from to_dynamo import UseDynamoDB

table_name = 'EventoCloudTrail_230'
index = 'userIdentity_userName-eventTime-index'

def main():
    db = UseDynamoDB("prueba")

    user = 'antonio'
    start_time = time.time()
    db.new_user(table_name, user)
    elapsed_time = time.time() - start_time
    print("Time elapsed for  items %f " % elapsed_time)

if (__name__ == '__main__'):
    main()
