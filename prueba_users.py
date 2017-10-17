import boto3
from to_dynamo import UseDynamoDB

table_name = 'EventoCloudTrail_230'
index = 'userIdentity_userName-eventTime-index'

def main():
    db = UseDynamoDB("prueba")
    event = {
        'eventID': '1',
        'users': 'yo, tu, el'
    }
    db.event_save_custom(table_name, event)

if (__name__ == '__main__'):
    main()
