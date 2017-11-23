
from boto3 import dynamodb
import boto3
import json, ast
import my_parser
import decimal
from boto3.dynamodb.conditions import Key
import settings

class UseDynamoDB:
    
    def __init__(self, name, verbose=False):
        self.name = name
        self.index = 'userIdentity_userName-eventTime-index'
        self.verbose = verbose


    
    def guardar_evento(self, name_table, event):

        #eventos = resource.Table(name_table)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(name_table)
        nameCamp = 'userIdentity_userName'
        # Creamos evento nuevo
        # datos = {
        #     'eventID':'b6b958b2-ff15-42b6-bc6d-c8e81a780dd7',
        #     'account_id':1,
        #     'hola':'adios'
        # }

        for datos in event.events():
            # print('Event name: {0}'.format(e['event_name']))
            # print('Event request: {0}'.format(e['request']))
            if self.verbose:
                print('Event request: {0}'.format(datos))

            name_event = datos.get("eventName", None)
            if name_event is None or name_event.lower().startswith(tuple(settings.filterEventNames)):
                print("Evento no")
                return

            userName = datos.get(nameCamp, None)
            if userName is None:
                datos[nameCamp] = 'no_user'

            #evento = Item(eventos, data=datos)
            table.put_item(
                Item=datos
            )
            
            # response = eventos.put_item(
            #     Item=datos
            # )
            if self.verbose:
                print("PutItem succeeded:")
            # print(json.dumps(response, indent=4))

            if userName is None or userName == ' ':
                continue

            self.new_user(name_table, userName)
            if self.verbose:
                print("User %s added to list" % userName)

    """Get old user and add a new user. if not exist yet"""
    def new_user(self, name_table,user):
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
            # Key={arr[0]: arr[1]},
            Key={
                'eventID': '1',
                'userIdentity_userName': 'all',
                # 'eventTime': '1',
                 # 'eventTime': '1'
            },
            UpdateExpression=("SET {0} = :p").format(setValue),
            ExpressionAttributeValues={
                ':p': users,
                # ':p': {user:'1'},
                # ':p': m,
            },
            ReturnValues="UPDATED_NEW"
            # ExpressionAttributeValues={':updated': 'UPDATED'}
        )

        # print(users)