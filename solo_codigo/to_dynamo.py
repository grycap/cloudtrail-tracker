
from boto.dynamodb2.table import Table
from boto.dynamodb2.items import Item
import my_parser

class UseDynamoDB:
    
    def __init__(self, name):
        self.name = name
    
    def guardar_evento(self, name_table, event=my_parser.Event('')):
        eventos = Table(name_table)

        # Creamos evento nuevo
        # datos = {
        #     'eventID':'b6b958b2-ff15-42b6-bc6d-c8e81a780dd7',
        #     'account_id':1,
        #     'hola':'adios'
        # }
        
        for e in event.events():
            # print('Event name: {0}'.format(e['event_name']))
            # print('Event request: {0}'.format(e['request']))
            print('Event request: {0}'.format(e))
        
            datos = e
            evento = Item(eventos, data=datos)
        
            evento.save()