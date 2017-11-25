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
import boto3
from boto3 import resource
from boto3.dynamodb.conditions import Key
import time
from operator import itemgetter
import settings

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')
table_name=settings.table_name
index = 'userIdentity_userName-eventTime-index'

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

def item_count():
    table = dynamodb_resource.Table(table_name)

    return table.item_count

"""Return a list of users"""
def users_list():
    listName = 'listUsers'
    pe = Key('eventID').eq('1') #what we want to search

    table = dynamodb_resource.Table(table_name)

    response = table.query(
        KeyConditionExpression=pe,
    )
    data = response['Items']
    users = list(data[0][listName].keys())
    #search_in_events(users,data,users_itemName)
    # print(users)
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ProjectionExpression=pe,
        )
        data= response['Items']
        users.append(list(data[0][listName].keys()))
        #search_in_events(users, data, users_itemName)
        # print(users)

    return users

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
time = YYYY-MM-DD or YYYY-MM-DDTHH-MM-SSZ
returns a number (int)"""
def actions_between_time(time1, time2, event=None,  request_parameter = None):
    time1 = format_time(time1)
    time2 = format_time(time2)

    total = 0
    users_l = users_list()
    if event is None:

        for user in users_l:
            total = total + used_services(user, time1, time2)
    else:
        for user in users_l:
            total = total + user_count_event(user, event, time1, time2,request_parameter=request_parameter)

    return total


"""Number of services used by an user between two times"""
def used_services(user, time1=None, time2=None):
    time1 = format_time(time1)
    time2 = format_time(time2)

    users_itemName = 'userIdentity_userName'
    eventTime = 'eventTime'

    # filter expression
    feAux = Key(users_itemName).eq(user);
    if time1 is not None and time2 is  not None:
        feAux = Key(users_itemName).eq(user) & Key(eventTime).between(time1, time2)
    table = dynamodb_resource.Table(table_name)
    response = table.query(
        IndexName=index,
        KeyConditionExpression=feAux ,
        Select='COUNT'
    )
    events = response['Count']
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            IndexName=index,
            KeyConditionExpression=feAux,
            Select='COUNT'
        )
        events = events + (response['Count'])


    return events

"""Count events from an user
Return number_of_events"""
def user_count_event(user, event, time1, time2, request_parameter = None):
    time1 = format_time(time1)
    time2 = format_time(time2)

    index = 'userIdentity_userName-eventTime-index'

    users_itemName = 'userIdentity_userName'
    eventName = 'eventName'
    eventTime = 'eventTime'

    feEvent = Key(eventName).eq(event);

    if request_parameter:
        request = request_parameter[0]
        parameter = request_parameter[1]
        feEvent = feEvent & Key(request).eq(parameter)

    feAux = Key(users_itemName).eq(user);
    table = dynamodb_resource.Table(table_name)
    response = table.query(
            IndexName=index,
            KeyConditionExpression=feAux & Key(eventTime).between(time1, time2) ,
            FilterExpression=feEvent,
            Select='COUNT'
    )
    events = response['Count']
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            IndexName=index,
            KeyConditionExpression=feAux & Key(eventTime).between(time1, time2),
            FilterExpression=feEvent,
            Select='COUNT'
         )
        events = events + (response['Count'])
    return events

"""Top users, return an ordered list of tuples with [('user',numOfActions)]"""
def top_users(time1, time2, event=None, request_parameter=None):
    time1 = format_time(time1)
    time2 = format_time(time2)
    resList = []

    users_l = users_list()
    if event is None:
        for user in users_l:
            events = used_services(user, time1, time2)
            resList.append((user,events))
    else:
        for user in users_l:
            events = user_count_event(user, event, time1, time2, request_parameter=request_parameter)
            resList.append((user,events))

    resList = sorted(resList, key=itemgetter(1))
    return list(reversed(resList))


def main():
    eventName = "RunInstances"
    request = ("requestParameters_instanceType", "m1.small")
    # pruebas2()

    # start_time = time.time()
    # user_events = user_count_event('grycap-aws',eventName,'2014-06-01T12:00:51Z','2017-06-01T19:00:51Z', request_parameter=request)
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for user_count_event items %f " % elapsed_time)

    # start_time = time.time()
    # user_events = used_services('alucloud171','2014-06-01T12:00:51Z', '2017-06-01T19:00:51Z' )
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for used_services items %f " % elapsed_time)

    # start_time = time.time()
    # user_events = users_list()
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for users_list items %f " % elapsed_time)

    # start_time = time.time()
    # user_events = top_users('2014-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for top_users items %f " % elapsed_time)


    # start_time = time.time()
    # user_events = actions_between_time( '2014-06-01T12:00:51Z','2018-06-01T19:00:51Z')
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for  actions_between_time (all events) %f " % elapsed_time)

    start_time = time.time()
    user_events = actions_between_time('2014-06-01T12:00:51Z', '2018-06-01T19:00:51Z',event='RunInstances', request_parameter=request)
    elapsed_time = time.time() - start_time
    print(user_events)
    print("Time elapsed for  actions_between_time (one event) %f " % elapsed_time)


if (__name__ == '__main__'):
    main()
