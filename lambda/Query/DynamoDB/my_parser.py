"""
formato eventos cloudtrail: http://docs.aws.amazon.com/es_es/awscloudtrail/latest/userguide/cloudtrail-event-reference.html
cambios en cloudtrail: http://docs.aws.amazon.com/es_es/awscloudtrail/latest/userguide/cloudtrail-document-history.html

tutorial dynamoDB: https://aws.amazon.com/es/getting-started/tutorials/create-nosql-table/


"""

import gzip
import json
import os
from decimal import *

def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            if (x == "" or x == None):
                x = " "
            #verifi if is a number and a decimal to pass as Decimal('')
            elif(isinstance(x,float)):
                x = Decimal(str(x))

            out[name[:-1]] = x

    flatten(y)
    return out

"""Clase para un solo archivo de eventos"""
class Event:
    
    CLOUDTRAIL_EVENT_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    
    def __init__(self, archive_base_dir):
        # store base dir to CloudTrail archives
        self.file = archive_base_dir.rstrip('/')
        fp = gzip.open(self.file, 'rt')
        self.all_events = json.loads(fp.read())
        fp.close()
        """Values that we want to store of an event"""
        self.selected = [
            "eventID",
            "userIdentity_userName",
            "awsRegion",
            "eventName",
            "eventSource",
            "eventTime",
            "eventType",
            "userAgent",
            "userIdentity_principalId",
            "requestParameters_bucketName",
            "requestParameters_dBInstanceIdentifier",
            "requestParameters_dBSecurityGroupName",
            "requestParameters_includeAllInstances",
            "requestParameters_includeDeleted",
            "requestParameters_instanceType",
            "requestParameters_roleSessionName",
            "requestParameters_volumeSet_items_0_volumeId",
            "responseElements_credentials_accessKeyId",
            "responseElements_credentials_expiration",
            "responseElements_credentials_sessionToken",

            # "userIdentity_type",
            # "userIdentity_accountId",
            # "userIdentity_arn",
            # "responseElements",
            # "userIdentity_accessKeyId",
            # "userIdentity_sessionContext_attributes_creationDate",
            # "userIdentity_sessionContext_attributes_mfaAuthenticated",
            # "userIdentity_invokedBy",
            # "resources_0_ARN",
            # "resources_0_accountId",
            # "resources_0_type",
            # "readOnly",
            # "requestParameters_encryptionContext_aws:lambda:FunctionArn",
            # "requestParameters_instancesSet_items_0_instanceId",
            # "requestParameters_filterSet_items_0_name",
            # "requestParameters_filterSet_items_0_valueSet_items_0_value",
            # "userIdentity_sessionContext_sessionIssuer_accountId",
            # "userIdentity_sessionContext_sessionIssuer_arn",
            # "userIdentity_sessionContext_sessionIssuer_principalId",
            # "userIdentity_sessionContext_sessionIssuer_type",
            # "userIdentity_sessionContext_sessionIssuer_userName",
            # "requestParameters",
            # "errorCode",
            # "errorMessage",
            # "requestParameters_maxRecords",
            # "requestParameters_accountAttributeNameSet_items_0_attributeName",
            # "requestParameters_availabilityZone",
            # "requestParameters_blockDeviceMapping_items_0_deviceName",
            # "requestParameters_blockDeviceMapping_items_0_ebs_deleteOnTermination",
            # "requestParameters_blockDeviceMapping_items_0_ebs_volumeSize",
            # "requestParameters_blockDeviceMapping_items_0_ebs_volumeType",
            # "requestParameters_clientToken",
            # "requestParameters_clusterId",
            # "requestParameters_disableApiTermination",
            # "requestParameters_environmentId",
            # "requestParameters_environmentIds_0",
            # "requestParameters_externalId",
            # "requestParameters_force",
            # "requestParameters_groupSet_items_0_groupId",
            # "requestParameters_instancesSet_items_0_imageId",
            # "requestParameters_instancesSet_items_0_keyName",
            # "requestParameters_instancesSet_items_0_maxCount",
            # "requestParameters_instancesSet_items_0_minCount",
            # "requestParameters_location_0",
            # "requestParameters_maxResults",
            # "requestParameters_monitoring_enabled",
            # "requestParameters_roleArn",
            # "responseElements_instancesSet_items_0_currentState_code",
            # "responseElements_instancesSet_items_0_currentState_name",
            # "responseElements_instancesSet_items_0_instanceId",
            # "responseElements_instancesSet_items_0_previousState_code",
            # "responseElements_instancesSet_items_0_previousState_name",
            # "sharedEventID",
            # "eventVersion",
            # "recipientAccountId",
            # "requestID",
            # "sourceIPAddress",
            # "responseElements_assumedRoleUser_arn",
            # "responseElements_assumedRoleUser_assumedRoleId",
            # "requestParameters_snapshotId",
            # "requestParameters_stackName",
        ]

    def count_events(self):
        return len(self.all_events['Records'])
    
    def events(self):

    
        if ('Records' in self.all_events):
        
            for trail_item in self.all_events['Records']:
                yield self.build_event(trail_item)

    """Function for select only the values that we are searching - 
    Filter """
    def select(self, flat={}):
        res = {}
        for k in self.selected:
            r = flat.get(k, None)
            if r:
                res[k] = r


        return res
    def build_event(self, source):
        # print("\n\n %s source" % source)
        flat = flatten_json(source)
        # f = json_normalize(flat)
        # print("\n %s flatten" % f)
        flat = self.select(flat)
        # print(flat)
        # exit()
        return flat

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
    path = "/home/jose/Documentos/TFG/muestras"
    # event = Event('/home/jose/Documentos/TFG/muestras/974349055189_CloudTrail_us-east-1_20170607T1510Z_kgD1yab9lfzZAzaQ.json.gz')
    for doc in os.listdir(path):
        event = Event("{}/{}".format(path, doc))
        # print("Num events %d " % event.count_events())
        for e in event.events():
            # print('Event name: {0}'.format(e['event_name']))
            # print('Event request: {0}'.format(e['request']))
            #rds.amazonaws.com
            if "rds" in e['eventSource']:
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
    