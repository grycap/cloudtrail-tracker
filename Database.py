"""Inits the database"""
import boto3
from boto3 import resource
import botocore
import time

dynamodb_resource = resource('dynamodb')



def init(table_name):
    create_table(table_name)
    add_users_row(table_name)

def create_table(table_name):
    table = dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'userIdentity_userName',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'eventTime',
                'AttributeType': 'S'
            },
        ],
        TableName=table_name,
        KeySchema=[

            {
                'AttributeName': 'userIdentity_userName',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'eventTime',
                'KeyType': 'RANGE'
            }
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
                "eventTime": "1",
                "userIdentity_userName": "all",
                "listUsers": {}

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

    init(table_name='EventoCloudTrail_V2')
