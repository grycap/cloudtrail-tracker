
from boto3 import dynamodb
import boto3
import json
import my_parser
import decimal

class UseDynamoDB:
    
    def __init__(self, name):
        self.name = name
    
    def guardar_evento(self, name_table, event=my_parser.Event('')):
        #eventos = resource.Table(name_table)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(name_table)
        # Creamos evento nuevo
        # datos = {
        #     'eventID':'b6b958b2-ff15-42b6-bc6d-c8e81a780dd7',
        #     'account_id':1,
        #     'hola':'adios'
        # }
        
        for datos in event.events():
            # print('Event name: {0}'.format(e['event_name']))
            # print('Event request: {0}'.format(e['request']))
            print('Event request: {0}'.format(datos))
            

            #evento = Item(eventos, data=datos)
            table.put_item(
                Item=datos
            )
            
            # response = eventos.put_item(
            #     Item=datos
            # )
            print("PutItem succeeded:")
            # print(json.dumps(response, indent=4))