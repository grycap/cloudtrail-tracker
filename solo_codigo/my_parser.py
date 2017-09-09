"""
formato eventos cloudtrail: http://docs.aws.amazon.com/es_es/awscloudtrail/latest/userguide/cloudtrail-event-reference.html
cambios en cloudtrail: http://docs.aws.amazon.com/es_es/awscloudtrail/latest/userguide/cloudtrail-document-history.html

tutorial dynamoDB: https://aws.amazon.com/es/getting-started/tutorials/create-nosql-table/


"""

from datetime import datetime
import gzip
import json
import os
import re

"""Clase para un solo archivo de eventos"""
class Event:
    
    CLOUDTRAIL_EVENT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    
    def __init__(self, archive_base_dir):
        # store base dir to CloudTrail archives
        self.file = archive_base_dir.rstrip('/')
    
    def events(self):
        fp = gzip.open(self.file , 'rt')
        all_events = json.loads(fp.read())
        fp.close()
    
        if ('Records' in all_events):
        
            for trail_item in all_events['Records']:
                yield self.build_event(trail_item)

    def build_event(self, source):
    
        # convert time string to datetime at UTC
        event_time_utc = (
            datetime.strptime(
                source['eventTime'],
                Parser.CLOUDTRAIL_EVENT_DATETIME_FORMAT
            )
        )
    
        # Recogida de datos aqui
        eventID = source['eventID']
    
        # extract the data we care about from the CloudTrail item into dict
        return {
            'eventID': eventID,
            'request': self.strip_data(source['requestParameters']),
            'response': self.strip_data(source['responseElements']),
            'account_id': str(source['recipientAccountId']),
            'region': str(source['awsRegion']),
            'event_name': str(source['eventName']),
            #'event_time': event_time_utc,
            #TODO poner un formato de tiempo valido para dynamoDB
    
            # 'principalId': str(principalID)
        }

    """Pasa los datos largos (listas, dicts, elementos simples..)
    a un solo objeto del mismo tipo"""

    def strip_data(self, data):
        data_type = type(data)
    
        # recursively process via strip_data() both list and dictionary structures
        if (data_type is list):
            return [
                self.strip_data(list_item)
                for list_item in data
            ]
    
        if (data_type is dict):
            return {
                self.strip_data(dict_key): self.strip_data(dict_value)
                for (dict_key, dict_value) in data.items()
            }
    
        if (data_type is str):
            # if unicode cast to string
            data = str(data)
    
        return data
    

class Parser:
    
    # Nombre archivos eventos cloudtrail
    ARCHIVE_FILENAME_REGEXP = re.compile(
        r'^[0-9]{12}_CloudTrail_[a-z]{2}-[a-z]+-[0-9]_[0-9]{8}T[0-9]{4}Z_[a-zA-Z0-9]{16}\.json\.gz$')
    
    CLOUDTRAIL_EVENT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, archive_base_dir):
        # store base dir to CloudTrail archives
        self.archive_base_dir = archive_base_dir.rstrip('/')
        print("init")

    def archive_file_list(self):
        for (base_path, dir_list, file_list) in os.walk(self.archive_base_dir):
            # work over files in directory
            for file_item in file_list:
                # does file item match archive pattern?
                if (not Parser.ARCHIVE_FILENAME_REGEXP.search(file_item)):
                    # nope - skip file
                    continue
            
                # full path to archive file
                yield '{0}/{1}'.format(base_path, file_item)

    def events(self):

        # work over CloudTrail archive files
        for file in self.archive_file_list():
            # open archive - parse JSON contents to dictionary
            fp = gzip.open(file, 'rt')
            all_events = json.loads(fp.read())
            fp.close()

            if ('Records' in all_events):

                for trail_item in all_events['Records']:
                    yield self.build_event(trail_item)

    def build_event(self, source):
  
        # convert time string to datetime at UTC
        event_time_utc = (
            datetime.strptime(
                source['eventTime'],
                Parser.CLOUDTRAIL_EVENT_DATETIME_FORMAT
            )
        )

        # Recogida de datos aqui
        eventID = source['eventID']
        
        # extract the data we care about from the CloudTrail item into dict
        return {
            'eventID': eventID,
            'request': self.strip_data(source['requestParameters']),
            'response': self.strip_data(source['responseElements']),
            'account_id': str(source['recipientAccountId']),
            'region': str(source['awsRegion']),
            'event_name': str(source['eventName']),
            #'event_time': event_time_utc,
            
            #'principalId': str(principalID)
        }

    """Pasa los datos largos (listas, dicts, elementos simples..)
    a un solo objeto del mismo tipo"""
    def strip_data(self, data):
        data_type = type(data)
    
        # recursively process via strip_data() both list and dictionary structures
        if (data_type is list):
            return [
                self.strip_data(list_item)
                for list_item in data
            ]
    
        if (data_type is dict):
            return {
                self.strip_data(dict_key): self.strip_data(dict_value)
                for (dict_key, dict_value) in data.items()
            }
    
        if (data_type is str):
            # if unicode cast to string
            data = str(data)
    
        return data

def main():
    print('Example')
    
    event = Event('974349055189_CloudTrail_us-east-1_20170601T0005Z_12nCTooUATtsirhW.json.gz')
    for e in event.events():
        # print('Event name: {0}'.format(e['event_name']))
        # print('Event request: {0}'.format(e['request']))
        print('Event request: {0}'.format(e))
    
    # parser = Parser('examples/')
    # for event in parser.events():
    #     print('Event name: {0}'.format(event['event_name']))
    #     print('Event request: {0}'.format(event['request']))
    #
    # for event in parser.events():
    #     print("---"*5)
    #     print('Event name: {0}'.format(event['event_name']))
    #     for i in event:
    #         print('{0} -> {1}'.format(i,event[i]))
    #     print("---" * 5)



if (__name__ == '__main__'):
    main()
    