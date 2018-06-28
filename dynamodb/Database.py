# CloudTrail-Tracker 
# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Inits the database"""
import boto3, sys, os
from boto3 import resource
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from settings import settings

table_name = settings.table_name
dynamodb_resource = resource('dynamodb')



def init(table_name):
    """
    Init all the DB
    :param table_name: String
    :return: None
    """
    print("Creating table %s " % table_name)
    create_table(table_name)
    print(". . .")
    print("Table created")
    add_users_row(table_name)
    print("Finished")

def create_table(table_name):
    """

    :param table_name: Creates the table on DynamoDB
    :return: None
    """
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


def add_users_row(name_table):
    """
    Add the especial user/services/params row.
    row with eventID = 1.
    rows = listUsers, services, cols
    :param name_table: String
    :return: None
    """
    print("Creating row for users, services and parameters list...")
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
            time.sleep(50)



    print("Succeeded")
    return

if (__name__ == '__main__'):
    init(table_name=settings.table_name)
