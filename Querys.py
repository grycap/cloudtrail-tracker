"""limits: http://docs.aws.amazon.com/es_es/amazondynamodb/latest/developerguide/HowItWorks.ProvisionedThroughput.html"""

from boto3 import resource
from boto3.dynamodb.conditions import Key

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')
table_name='EventoCloudTrail_230'

def get_table_metadata(table_name):
    """
    Get some metadata about chosen table.
    """
    table = dynamodb_resource.Table(table_name)

    return {
        'num_items': table.item_count,
        'primary_key_name': table.key_schema[0],
        'status': table.table_status,
        'bytes_size': table.table_size_bytes,
        'global_secondary_indices': table.global_secondary_indexes
    }

def read_table_item(table_name, pk_name, pk_value):
    """
    Return item read by primary key.
    """
    table = dynamodb_resource.Table(table_name)
    response = table.get_item(Key={pk_name: pk_value})



    return response

def scan_table(table_name, filter_key=None, filter_value=None):
    """
    Perform a scan operation on table.
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = dynamodb_resource.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.scan(FilterExpression=filtering_exp)

        events = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],FilterExpression=filtering_exp)
            events.extend(response['Items'])

            # print(users)
    else:
        response = table.scan()

        events = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            events.extend(response['Items'])

            # print(users)



    return events


def query_table(table_name, filter_key=None, filter_value=None):
    """
    Perform a query operation on the table. 
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = dynamodb_resource.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response


"""Return a dict :   {'UserX': 'number of actions/events', ...} """
def users_list():
    users_itemName = 'userIdentity_userName'

    pe = users_itemName #what we want to search

    table = dynamodb_resource.Table(table_name)

    users = dict()

    response = table.scan(ProjectionExpression=pe,)
    data = response['Items']

    search_in_events(users,data,users_itemName)
    # print(users)
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],ProjectionExpression=pe,)
        data= response['Items']
        search_in_events(users, data, users_itemName)
        # print(users)

    print("- Users- \n %s " % users)
    exit()

    return data

"""Search atrib in list of events"""
def search_in_events(result=dict(), events=list(), attrib=''):

    for e in events:
        u = e.get(attrib, None)
        if u is None:
            pass
            #Events without that atrib
        else:
            nums = result.get(u,0)
            result[u] = nums + 1

    return result

"""YYYY-MM-DD to YYYY-MM-DDTHH-MM-SSZ only when its necessary """
def format_time(time):
    if len(time) == 10:
        time = time + "T00:00:00Z"

    if len(time) != 20:
        raise Exception("Error on time format!")

    return time

"""all actions between time1 and time2
time = YYYY-MM-DD or YYYY-MM-DDTHH-MM-SSZ,
Return, userIdentity_userName, eventName, Evntsource, eventTime """
def actions_between_time(time1, time2):

    time1 = format_time(time1)
    time2 = format_time(time2)

    users_itemName = 'userIdentity_userName'
    eventName = 'eventName'
    eventSource = 'eventSource'
    eventTime = 'eventTime'

    pe = users_itemName + ", " + eventName + ", " + eventSource + ", " + eventTime
    #filter expression
    fe = Key(eventTime).between(time1, time2);

    table = dynamodb_resource.Table(table_name)
    response = table.scan(
        ProjectionExpression = pe,
        # ScanFilter=Key('eventTime').between(time1, time2)
        FilterExpression=fe,
    )
    events = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],ProjectionExpression=pe,)
        events.extend(response['Items'])

        # print(users)

    return events




def main():
    # table_name = 'EventoCloudTrail_230'
    info = get_table_metadata('EventoCloudTrail_230')
    print(info)
    # a = actions_between_time('2017-01-01T14:35:21Z','2017-10-01T14:35:21Z')
    # print(a)
    # print(len(a))
    all = scan_table(table_name)

    # print(all)
    # print(len(all))


if (__name__ == '__main__'):
    main()