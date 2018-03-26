"""Inits the database"""
import boto3, sys, os
from boto3 import resource
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from settings import settings

table_name = settings.table_name
dynamodb_resource = resource('dynamodb')



def init(table_name):
    print("Creating table %s " % table_name)
    create_table(table_name)
    add_users_row(table_name)

def create_table(table_name):
    table = dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'eventID',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'userIdentity_userName',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'eventTime',
                'AttributeType': 'S'
            }
        ],
        TableName=table_name,
        KeySchema=[

            {
                'AttributeName': 'eventID',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'userIdentity_userName',
                'KeyType': 'RANGE'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'userIdentity_userName-eventTime-index',
                'KeySchema': [
                    {
                        'AttributeName': 'userIdentity_userName',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'eventTime',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'

                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    print("Table status:", table.table_status)


def add_users_row(name_table):
    print("Creating row for user counting...")
    dynamodb_client = boto3.client('dynamodb')
    res = None
    while res is None:
        intent = 0
        try:
            table = dynamodb_resource.Table(name_table)
            datos = {
                "eventID": "1",
                "eventTime": "1",
                "userIdentity_userName": "all",
                "listUsers": {},
                "services": {},
                "cols": {}

            }
            res = table.put_item(
                Item=datos
            )
        except dynamodb_client.exceptions.ResourceNotFoundException:
            if intent > 50:
                print("Error adding users row")
                return
            intent += 1
            res = None
            print(". . .")
            time.sleep(5)



    print("Succeded: %s " % res)
    return

if (__name__ == '__main__'):
    init(table_name=settings.table_name)
