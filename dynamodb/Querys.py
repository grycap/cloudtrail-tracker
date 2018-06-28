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
import time, os , sys
from operator import itemgetter
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from settings import settings

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')
table_name=settings.table_name
index = settings.index

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


def users_list():
    """Return a list of users"""
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

def services_list():
    """Return a list of services"""
    listName = 'services'
    pe = Key('eventID').eq('1') #what we want to search

    table = dynamodb_resource.Table(table_name)

    response = table.query(
        KeyConditionExpression=pe,
    )
    data = response['Items']
    services = list(data[0][listName].keys())
    #search_in_events(users,data,users_itemName)
    # print(users)
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ProjectionExpression=pe,
        )
        data= response['Items']
        services.append(list(data[0][listName].keys()))
        #search_in_events(users, data, users_itemName)
        # print(users)

    return services

def parameters_list():
    """Return a list of parameters to query"""
    listName = 'cols'
    pe = Key('eventID').eq('1') #what we want to search

    table = dynamodb_resource.Table(table_name)

    response = table.query(
        KeyConditionExpression=pe,
    )
    data = response['Items']
    parameters = list(data[0][listName].keys())
    #search_in_events(users,data,users_itemName)
    # print(users)
    while 'LastEvaluatedKey' in response:
        response = table.query(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            ProjectionExpression=pe,
        )
        data= response['Items']
        parameters.append(list(data[0][listName].keys()))
        #search_in_events(users, data, users_itemName)
        # print(users)

    return parameters

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
    if(not time): return None
    if type(time) == str:
        if len(time) == 10:
            time = time + "T00:00:00Z"

        elif len(time) == 19:
            time = time + "Z"

        if len(time) != 20:
            raise Exception("Error on time format!")
    else:
        time = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    return time

def actions_between_time(time1, time2, event=None,  request_parameter = None, count= False,  begin_with=False):
    """all actions between time1 and time2
    time = YYYY-MM-DD or YYYY-MM-DDTHH-MM-SSZ
    returns a number (int)"""
    time1 = format_time(time1)
    time2 = format_time(time2)


    users_l = users_list()
    if event is None:
        if request_parameter:
            total = 0
            if count:
                for user in users_l:
                    total = total + used_services_parameter(user, request_parameter, time1=time1, time2=time2, count=True)
            else:
                total = []
                for user in users_l:
                    total.extend(used_services_parameter(user, request_parameter, time1=time1, time2=time2, count=False))
        else:
            total = 0
            if count:
                for user in users_l:
                    total = total + used_services(user, time1, time2, count= count)
            else:
                total = []
                for user in users_l:
                    total.extend(used_services(user, time1, time2, count= count))
    else:
        total = 0
        if count:
            for user in users_l:
                total = total + user_count_event(user, event, time1, time2, request_parameter=request_parameter, count=count,  begin_with=begin_with)

        else:
            total = []
            for user in users_l:
                total.extend(user_count_event(user, event, time1, time2,request_parameter=request_parameter, count=count, begin_with=begin_with))

    return total


def used_services(user, time1=None, time2=None,count=False):
    """Number of services used by an user between two times"""

    time1 = format_time(time1)
    time2 = format_time(time2)

    users_itemName = 'userIdentity_userName'
    eventTime = 'eventTime'
    eventsource = "eventSource"
    eventName = "eventName"
    eventID = "eventID"

    # filter expression
    feAux = Key(users_itemName).eq(user);
    if time1 is not None and time2 is  not None:
        feAux = Key(users_itemName).eq(user) & Key(eventTime).between(time1, time2)

    table = dynamodb_resource.Table(table_name)

    if count :

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
    else:
        pe = "{0}, {1}, {2}, {3}, {4}".format(users_itemName, eventTime, eventsource, eventName, eventID)
        response = table.query(
            IndexName=index,
            KeyConditionExpression=feAux,
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression=pe

        )

        events = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.query(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                IndexName=index,
                KeyConditionExpression=feAux,
                Select='SPECIFIC_ATTRIBUTES',
                ProjectionExpression=pe
            )
            events.extend(response['Items'])


    return events

def used_services_parameter(user, request_parameter, time1=None, time2=None, count=False):
    """Number of services used by an user between two times"""
    time1 = format_time(time1)
    time2 = format_time(time2)

    users_itemName = 'userIdentity_userName'
    eventTime = 'eventTime'
    eventsource = "eventSource"
    eventName = "eventName"
    eventID = "eventID"

    # filter expression
    feAux = Key(users_itemName).eq(user);
    if time1 is not None and time2 is not None:
        feAux = Key(users_itemName).eq(user) & Key(eventTime).between(time1, time2)
    if request_parameter:
        requests = request_parameter[0]
        parameters = request_parameter[1]
        feEvent = Key(requests[0]).eq(parameters[0])
        for i in range(1,len(requests)):
            feEvent = feEvent & Key(requests[i]).eq(parameters[i])

    table = dynamodb_resource.Table(table_name)

    if count:

        response = table.query(
            IndexName=index,
            KeyConditionExpression=feAux,
            FilterExpression=feEvent,
            Select='COUNT'
        )
        events = response['Count']
        while 'LastEvaluatedKey' in response:
            response = table.query(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                IndexName=index,
                KeyConditionExpression=feAux,
                FilterExpression=feEvent,
                Select='COUNT'
            )
            events = events + (response['Count'])

    else:
        pe = "{0}, {1}, {2}, {3}, {4}".format(users_itemName, eventTime, eventsource, eventName, eventID)
        response = table.query(
            IndexName=index,
            KeyConditionExpression=feAux,
            Select='SPECIFIC_ATTRIBUTES',
            FilterExpression=feEvent,
            ProjectionExpression=pe

        )
        events = response['Items']
        while 'LastEvaluatedKey' in response:

            response = table.query(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                IndexName=index,
                KeyConditionExpression=feAux,
                Select='SPECIFIC_ATTRIBUTES',
                FilterExpression=feEvent,
                ProjectionExpression=pe
            )
            events.extend(response['Items'])

    return events


def user_count_event(user, event, time1, time2, request_parameter = None, count=False, begin_with=False):
    """Events from an user
    Return_events"""
    time1 = format_time(time1)
    time2 = format_time(time2)

    index = 'userIdentity_userName-eventTime-index'

    users_itemName = 'userIdentity_userName'
    eventName = 'eventName'
    eventTime = 'eventTime'
    eventsource = "eventSource"
    eventID = "eventID"

    if not begin_with:
        feEvent = Key(eventName).eq(event);
    else:
        feEvent = Key(eventName).begins_with(event);

    if request_parameter:
        requests = request_parameter[0]
        parameters = request_parameter[1]
        for i in range(0,len(requests)):
            feEvent = feEvent & Key(requests[i]).eq(parameters[i])

    feAux = Key(users_itemName).eq(user);
    table = dynamodb_resource.Table(table_name)
    if count:
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
    else:
        pe = "{0}, {1}, {2}, {3}, {4}".format(users_itemName, eventTime, eventsource, eventName, eventID)
        response = table.query(
            IndexName=index,
            KeyConditionExpression=feAux & Key(eventTime).between(time1, time2),
            FilterExpression=feEvent,
            Select='SPECIFIC_ATTRIBUTES',
            ProjectionExpression=pe

        )

        events = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.query(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                IndexName=index,
                KeyConditionExpression=feAux & Key(eventTime).between(time1, time2),
                FilterExpression=feEvent,
                ProjectionExpression=pe,
                Select='SPECIFIC_ATTRIBUTES',
            )
            events.extend(response['Items'])
    return events

"""Top users, return an ordered list of tuples with [('user',numOfActions)]"""
def top_users(time1, time2, event=None, request_parameter=None,  begin_with=False):
    time1 = format_time(time1)
    time2 = format_time(time2)
    resList = []

    users_l = users_list()
    if event is None:
        if request_parameter is not None:
            for user in users_l:
                events = used_services_parameter(user,request_parameter, time1, time2, count=False)
                resList.append((user, events))
        else:
            for user in users_l:
                events = used_services(user, time1, time2)
                resList.append((user,events))
    else:
        for user in users_l:
            events = user_count_event(user, event, time1, time2, request_parameter=request_parameter, begin_with=begin_with)
            resList.append((user,events))

    resList = sorted(resList, key=itemgetter(1))
    return list(reversed(resList))

def remove_one(id, user):
    table = dynamodb_resource.Table(table_name)
    response = table.delete_item(
        Key={'eventID':id,
             'userIdentity_userName': user},

    )

def delete_events(frm, to , event, step=100):
    print("Querying event. . .")
    events = actions_between_time(frm, to, event=event)
    print("Deleting event. {} events to delete".format(len(events)))
    num = 0
    for e in events:
        id = e.get("eventID")
        user = e.get("userIdentity_userName")
        remove_one(id, user)
        num = num + 1
        if num % step == 0:
            print("{} events deleted.".format(num))


def main():
    eventName = "CreateDBInstance"
    request = (["requestParameters_instanceType"], ["t1.micro"])
    # request = None

    # start_time = time.time()
    # list_users = users_list()
    # elapsed_time = time.time() - start_time
    # print(list_users)
    # print("Time elapsed for user lists %f " % elapsed_time)
    #
    # start_time = time.time()
    # list_services = services_list()
    # elapsed_time = time.time() - start_time
    # print(list_services)
    # print("Time elapsed for services list  %f " % elapsed_time)
    #
    # start_time = time.time()
    # list_parameters = parameters_list()
    # elapsed_time = time.time() - start_time
    # print(list_parameters)
    # print("Time elapsed for services list  %f " % elapsed_time)

    start_time = time.time()
    user_events = user_count_event('alucloud178',eventName,
                                   '2014-06-01T12:00:51Z','2017-06-01T19:00:51Z',
                                   # request_parameter=[["eventSource"],["ec2"+".amazonaws.com"]],
                                   # count=True,
                                   begin_with=True
                                   )
    elapsed_time = time.time() - start_time
    print(user_events)
    print("Time elapsed for user_count_event items %f " % elapsed_time)
    #
    # start_time = time.time()
    # user_events = used_services('alucloud171','2014-06-01T12:00:51Z', '2017-06-01T19:00:51Z', count=False)
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for used_services items %f " % elapsed_time)

    # start_time = time.time()
    # user_events = used_services_parameter('gmolto', request, '2014-06-01T12:00:51Z', '2018-06-01T19:00:51Z', count=False)
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for used_services_parameter items %f " % elapsed_time)


    # start_time = time.time()
    # user_events = users_list()
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for users_list items %f " % elapsed_time)

    # start_time = time.time()
    # user_events = top_users('2014-06-01T12:00:51Z', '2017-06-01T19:00:51Z',request_parameter=request)
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for top_users items %f " % elapsed_time)


    # start_time = time.time()
    # user_events = actions_between_time( '2018-03-01Z16:15:15','2018-05-22T19:00:51Z', event=None, request_parameter=[["eventSource"],["ec2"+".amazonaws.com"]])
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for  actions_between_time (all events) %f " % elapsed_time)

    # start_time = time.time()
    # user_events = actions_between_time('2017-06-01T12:00:51Z', '2017-07-01T19:00:51Z',event='RunInstances', request_parameter=request, count=False)
    # elapsed_time = time.time() - start_time
    # print(user_events)
    # print("Time elapsed for  actions_between_time (one event) %f " % elapsed_time)

    # start_time = time.time()
    # delete_events( '2014-05-01Z16:15:15','2018-07-06T19:00:51Z', "AssumeRole")
    # elapsed_time = time.time() - start_time
    #
    # print("Time elapsed for  actions_between_time (all events) %f " % elapsed_time)


if (__name__ == '__main__'):
    main()
