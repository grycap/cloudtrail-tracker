from boto3 import resource
from boto3.dynamodb.conditions import Key

# The boto3 dynamoDB resource
dynamodb_resource = resource('dynamodb')

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
    else:
        response = table.scan()

    return response


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
def users_list(table_name='EventoCloudTrail_230'):
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

def main():
    # table_name = 'EventoCloudTrail_230'
    info = get_table_metadata('EventoCloudTrail_230')
    print(info)
    # exec_query('EventoCloudTrail_230','eventID','e662c7ab-b815-4d0d-967b-21a6cc47af78')
    # q = query_table('EventoCloudTrail_230','eventID','7589e218-be95-48bc-b8c8-435e519eaa2b')
    # print("Results from query %s " % q)
    #
    # scan = scan_table('EventoCloudTrail_230','eventID','7589e218-be95-48bc-b8c8-435e519eaa2b')
    # print("Results from scan %s " % scan)
    # print("count %d " % scan.get('Count'))
    #
    # user_id = '974349055189'
    # user = scan_table(table_name,'userIdentity_accountId',user_id)
    # print("User %s info \n %s \n Count %s" % (user_id, user, user.get('Count')))

    users_l = users_list()
    print("List of users %s" % users_l)
    print("List of users %s" % users_l.get('Count'))

if (__name__ == '__main__'):
    main()