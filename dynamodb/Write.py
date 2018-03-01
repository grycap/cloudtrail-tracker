
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
                return

            userName = datos.get(nameCamp, None)
            if userName is None:
                datos[nameCamp] = 'no_user'

            table.put_item(
                Item=datos
            )

            if self.verbose:
                print("PutItem succeeded:")

            if userName is None or userName == ' ':
                continue

            self.new_user(name_table, userName)
            if self.verbose:
                print("User %s added to list" % userName)


    def new_user(self, name_table,user):
        """Get old user and add a new user. if not exist yet"""
        index = 'userIdentity_userName'
        setValue = 'listUsers'
        arr = ['userIdentity_userName','all']
        # eventos = resource.Table(name_table)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(name_table)

        # filter expression
        fe = Key(arr[0]).eq(arr[1]);
        response = table.query(
            IndexName=self.index ,
            KeyConditionExpression=fe,
        )
        users = response['Items'][0][setValue]
        # users = ast.literal_eval(users)
        if users.get(user,None) is not None: return
        users[user] = '1'
        #update
        table.update_item(
            Key={
                'eventID': '1',
                'userIdentity_userName': 'all',
            },
            UpdateExpression=("SET {0} = :p").format(setValue),
            ExpressionAttributeValues={
                ':p': users,
            },
            ReturnValues="UPDATED_NEW"
        )

        # print(users)

if __name__ == '__main__':
    print(settings.filterEventNames)