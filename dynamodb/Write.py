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
import boto3
import os, sys
from boto3.dynamodb.conditions import Key
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import settings


class UseDynamoDB:
    """Class used to store items on DynamoDB"""
    
    def __init__(self, name, verbose=False):
        self.name = name
        self.index = settings.index
        self.verbose = verbose


    
    def store_event(self, name_table, event):

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(name_table)
        nameCamp = 'userIdentity_userName'

        for datos in event.events():
            """Every event file has one or more events"""
            if self.verbose:
                print('Event request: {0}'.format(datos))

            name_event = datos.get("eventName", None)
            if name_event is None or name_event.lower().startswith(tuple(settings.filterEventNames)):
                # print("Evento no")
                continue

            userName = datos.get(nameCamp, None)
            if userName is None:
                datos[nameCamp] = 'no_user'

            table.put_item(
                Item=datos
            )

            if self.verbose:
                print("PutItem succeeded:")

            ## Adding new user
            if userName is None or userName == ' ':
                userName = 'no_user'

            ## Adding a new service
            service_name = datos.get("eventSource", None)
            if service_name:
                service_name = service_name.split(".")[0]

            ## Ading columns
            columns = datos.keys()

            ## Adding all
            self.news(name_table, userName, service_name, columns)

    def news(self, name_table, user, service, new_columns):
        """Get an user and add it if not exist yet"""
        index = 'userIdentity_userName'
        setValue_cols = 'cols'
        setValue_services  = 'services'
        setValue_listUsers = 'listUsers'
        arr = ['userIdentity_userName', 'all']
        # eventos = resource.Table(name_table)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(name_table)

        # filter expression
        fe = Key(arr[0]).eq(arr[1]);
        response = table.query(
            IndexName=self.index,
            KeyConditionExpression=fe,
        )
        cols = response['Items'][0][setValue_cols]
        services = response['Items'][0][setValue_services]
        users = response['Items'][0][setValue_listUsers]
        # users = ast.literal_eval(users)
        aux = False
        for column in new_columns:
            if cols.get(column, None) is None:
                aux = True
                cols[column] = '1'

        if users.get(user,None) is None:
            aux = True
            users[user] = '1'

        if services.get(service, None) is None:
            aux = True
            services[service] = '1'

        if not aux: return
        # update
        table.update_item(
            Key={
                'eventID': '1',
                'userIdentity_userName': 'all',
            },
            UpdateExpression=("SET {0} = :p, {1} = :r, {2} = :q").format(setValue_cols, setValue_services, setValue_listUsers),
            ExpressionAttributeValues={
                ':p': cols,
                ':r': services,
                ':q': users,
            },
            ReturnValues="UPDATED_NEW"
        )


if __name__ == '__main__':
    print(settings.filterEventNames)