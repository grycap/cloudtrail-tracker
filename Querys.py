"""limits: http://docs.aws.amazon.com/es_es/amazondynamodb/latest/developerguide/HowItWorks.ProvisionedThroughput.html

List methods:
get metadata from table : get_table_metadata(table_name)
read item (one atrib) from table by pk: scan_table(table_name, filter_key, filter_value)
the same but by any key: scan_table(table_name, filter_key, filter_value)
list all users: users_list()
get events between two dates: actions_between_time(time1, time2)
services used by an user: used_services(user, time1, time2)
list of all services used from an user (return list_events(dict) and count_events(list)): user_count_event(user, event, time1, time2)
list a top user using services. 
    -> Return dict (k:user_name, v: list of events) and ordered list ((user_name,number_actions),..): top_users(time1, time2, event=None)


aux methods:
search in a list of events (dict format): search_in_events(dict, events, attrib)
format/validate time format: format_time(time)
"""

from boto3 import resource
from boto3.dynamodb.conditions import Key
import time

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
    if(time is None): return None
    if len(time) == 10:
        time = time + "T00:00:00Z"

    if len(time) != 20:
        raise Exception("Error on time format!")

    return time

"""all actions between time1 and time2
time = YYYY-MM-DD or YYYY-MM-DDTHH-MM-SSZ,
Return, userIdentity_userName, eventName, Evntsource, eventTime """
def actions_between_time(time1, time2, feAux = None):
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

    if feAux is not None:
        fe_complete = fe & feAux
    else:
        fe_complete = fe

    response = table.scan(
        # ProjectionExpression = pe,
        Select='COUNT',
        # ScanFilter=Key('eventTime').between(time1, time2)
        FilterExpression=fe_complete,
    )
    events = response['Count']
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],
                              # ProjectionExpression=pe,
                              Select='COUNT',
                              FilterExpression=fe_complete,)
        events = events + (response['Count'])

    return events

"""Number of services used by an user between two times"""
def used_services(user, time1 = None, time2 = None):
    time1 = format_time(time1)
    time2 = format_time(time2)

    users_itemName = 'userIdentity_userName'
    eventName = 'eventName'
    eventSource = 'eventSource'
    eventTime = 'eventTime'

    pe = users_itemName + ", " + eventName + ", " + eventSource + ", " + eventTime
    # filter expression
    fe2 = Key(users_itemName).eq(user);
    if time1 and time2:

        fe = Key(eventTime).between(time1, time2);

        table = dynamodb_resource.Table(table_name)
        response = table.scan(
            # ProjectionExpression=pe,
            # ScanFilter=Key('eventTime').between(time1, time2)
            Select='COUNT',
            FilterExpression=fe & fe2,
        )
        events = response['Count']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],
                                  # ProjectionExpression=pe,
                                  Select='COUNT',
                                  FilterExpression=fe & fe2,)
            events = events + (response['Count'])
    else:
        fe2 = Key(users_itemName).eq(user);
        table = dynamodb_resource.Table(table_name)
        response = table.scan(
            # ProjectionExpression=pe,
            # ScanFilter=Key('eventTime').between(time1, time2)
            Select='COUNT',
            FilterExpression=fe2,
        )
        print(response)
        events =  response['Count']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'],
                                  # ProjectionExpression=pe,
                                  Select='COUNT',
                                  FilterExpression=fe2 )
            events = events + (response['Count'])
            print(response)
        # print(users)

    return events

"""Count events from an user
Return events, number_of_events"""
def user_count_event(user, event, time1, time2):
    event_search = 'eventName'
    time2 = format_time(time2)

    index_name = 'eventID'
    index = 'userIdentity_userName-eventTime-index'
    time = 'eventTime'

    users_itemName = 'userIdentity_userName'
    eventName = 'eventName'
    eventSource = 'eventSource'
    eventTime = 'eventTime'

    pe = users_itemName + ", " + eventName + ", " + eventSource + ", " + eventTime
    # filter expression
    fe2 = Key(users_itemName).eq(user);
    fe3 = Key(event_search).eq(event);
    fe = Key(eventTime).between(time1, time2);
    feAux = Key(users_itemName).eq(user);
    fe_complete = fe & fe2 & fe3
    table = dynamodb_resource.Table(table_name)
    response = table.query(
            IndexName=index,
    # ProjectionExpression=pe,
            KeyConditionExpression=feAux & Key(eventTime).between(time1, time2),
            # FilterExpression= fe_complete,
            Select='COUNT'
    )
    print(response)
    events = response['Count']
    while 'LastEvaluatedKey' in response:
        response = table.query(ExclusiveStartKey=response['LastEvaluatedKey'],
                              # ProjectionExpression=pe,
                              FilterExpression=fe_complete,
                              Select='COUNT'
                              )
        events = events + (response['Count'])
    return events

"""Top users"""
def top_users(time1, time2, event=None):
    """aux method, return two dict - 
    user and his events
    user and his number of total events (counted)"""
    def events_per_users(events):
        print("-> Events per user")
        # usera key = user
        #value = list of events
        users_events = dict()
        users_events_count = dict()
        for e in events:
            user = e.get('userIdentity_userName',None)
            if(user is None): continue #not all events have an user
            event = e['eventName']
            levent_user = users_events.get(user,[])
            n_events_user = users_events_count.get(user,0)

            levent_user.append(event)
            n_events_user = n_events_user + 1

            users_events[user] = levent_user
            users_events_count[user] = n_events_user

        return users_events,users_events_count

    if not event:
        actions = actions_between_time(time1, time2)
        print("Actions between time done")

    else:
        fe_aux = Key('eventName').eq(event);
        actions = actions_between_time(time1, time2, feAux= fe_aux)
    print("events per user to do")
    users_events, users_events_count = events_per_users(actions)
    print("-"*10)
    list_ordered_top_events = []


    for key, value in users_events_count.items():
        list_ordered_top_events.append([key,value])
    list_ordered_top_events = sorted(list_ordered_top_events, key=lambda x: -x[1])

    return actions,list_ordered_top_events

def main():
    # table_name = 'EventoCloudTrail_230'
    # info = get_table_metadata('EventoCloudTrail_230')
    # print(info)
    # a = actions_between_time('2017-01-01T14:35:21Z','2017-10-01T14:35:21Z')
    # print(a)
    # print(len(a))

    # start_time = time.time()
    # all = scan_table(table_name)
    # elapsed_time = time.time() - start_time
    # print("Time elapsed for all items %f " % elapsed_time)
    start_time = time.time()
    # alucloud171
    user_events = user_count_event('gmolto','DescribeMetricFilters','2017-06-01T12:00:51Z','2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    print("Top users")
    print(user_events)
    print("Time elapsed for  items %f " % elapsed_time)


    # print(all)
    # print(len(all))


if (__name__ == '__main__'):
    main()