from __future__ import print_function
import boto3
import os
import sys, ast
import uuid, json, time, datetime
from dynamodb import Querys
# import requests

"""YYYY-MM-DD to YYYY-MM-DDTHH-MM-SSZ only when its necessary """
def format_time(time):
    if(not time): return None
    if len(time) == 10:
        time = time + "T00:00:00Z"

    if len(time) != 20:
        raise Exception("Error on time format!")

    return time

select = [
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
]

def get_request_parameters(event):
    request = event.get("params", None)
    parameter = event.get("values", None)
    request_parameters = None
    if request and parameter:
        try:
            request =  ast.literal_eval(request)
            parameter =  ast.literal_eval(parameter)
        except ValueError:
            pass
        requests = []
        parameters = []
        if type(request) == list:
            #something
            pass
        elif type(request) == str:
            request = request.split(",")
            parameter = parameter.split(",")

        for i in range(len(request)):
            r = request[i]
            p = parameter[i]

            if "requestParameters_" + r in select:
                requests.append("requestParameters_" + r)
            elif "responseElements_" + r in select:
                requests.append("responseElements_" + r)
            else:
                requests.append(r)
            parameters.append(p)
        request_parameters = [requests, parameters]
    return request_parameters


def handler(event, context):

    if event.get("list_users", None):
        return action("users_list")

    request_parameters = get_request_parameters(event)


    event_name = event.get("eventName",None)
    user_name = event.get("user",None)
    service = event.get("service",None)
    count = event.get("count",False)
    time1 = format_time(event.get("from",None))
    time2 = format_time(event.get("to",None))

    if not count or count == "false" or count == "False":
        count = False
    if not event_name:
        event_name = None
    if not service:
        service = None
    if not time1:
        time1 = time.strftime("%Y-%m-%d")
    if not time2:
        date_1 = datetime.datetime.strptime(time1, "%Y-%m-%d")
        time2 = date_1 + datetime.timedelta(days = 7)
        time2 = time2.strftime("%Y-%m-%d")

    #Select action
    if user_name and not service:
        #used_services or used_services_parameter or user_count_event
        if not event_name:
            if request_parameters:
                method = "used_services_parameter"
            else:
                method = "used_services"
        else:
            method = "user_count_event"
    elif service and not user_name:
        #actions_between
        method = "actions_between"
        if request_parameters:
            requests, parameters = request_parameters
            requests.append("eventSource")
            parameters.append(service+".amazonaws.com")
            request_parameters = [requests, parameters]
        else:
            request_parameters = [["eventSource"],[service+".amazonaws.com"]]
        # return "{} {} {} {} {} {} {} {}".format(method, user_name, time1, time2, event_name, request_parameters[0], request_parameters[1], count)

    else:
        return json.dumps("Error")
    print(method)
    print(request_parameters)
    return action(method, user_name=user_name, time1=time1, time2=time2, event_name=event_name, request_parameters=request_parameters, count=count)

def action(method, user_name=None, time1=None, time2=None, event_name=None, request_parameters=None, count=False):

    if method == "actions_between":
        return json.dumps(Querys.actions_between_time(
            time1,
            time2,
            event=event_name,
            request_parameter=request_parameters,
            count=count
        ))
    elif method == "used_services":
        return json.dumps(
            Querys.used_services(user_name, time1, time2, count)

        )

    elif method == "used_services_parameter":
        return json.dumps(
            Querys.used_services_parameter(
                user_name, request_parameters, time1, time2, count
            )

        )

    elif method == "user_count_event":
        return json.dumps((
            Querys.user_count_event(user_name, event_name, time1, time2, request_parameters, count)

        ))

    elif method == "top_users":
        return json.dumps(
            Querys.top_users(time1, time2, event_name, request_parameters)
        )

    elif method == "users_list":
        return json.dumps(Querys.users_list())



    return "Error: {}".format(event.keys())


if __name__ == '__main__':
    event = {
    "user":  "gmolto",
    "service": "",
    "count":  "",
    "eventName":  "",
    "from":  "2016-06-01",
    "to":  "2017-09-01",
    # "params":  "['instanceType']",
    "params":  "instanceType,eventSource",
    # "values":  "['m1.small']"
    "values":  "m1.small,ec2.amazonaws.com"
    }
    res = handler(event, None)
    print(res)