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
def handler(event, context):

    if event.get("list_users", None):
        return action("users_list")

    # type = event.get("type",None)
    request = event.get("param",None)
    print(request)
    parameter = event.get("value",None)

    if request and parameter:
        request =  ast.literal_eval(request)
        parameter=  ast.literal_eval(parameter)
        requests = []
        parameters = []
        for i in range(len(request)):
            r = request[i]
            p = parameter[i]
            if r in select:
                requests.append(r)
                parameters.append(p)
            elif "requestParameters_"+r in select:
                requests.append("requestParameters_"+r)
                parameters.append(p)

        request_parameters = [requests, parameters]
    else:
        request_parameters = None

    event_name = event.get("eventName",None)
    user_name = event.get("user",None)
    service = event.get("service",None)
    count = event.get("count",False)
    time1 = format_time(event.get("from",None))
    time2 = format_time(event.get("to",None))

    if not count :
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
            if parameter:
                type = "used_services_parameter"
            else:
                type = "used_services"
        else:
            type = "user_count_event"
    elif service and not user_name:
        #actions_between
        type = "actions_between"
        if request_parameters:
            requests, parameters = request_parameters
            requests.append("eventSource")
            parameters.append(service+".amazonaws.com")
            request_parameters = [requests, parameters]
        else:
            request_parameters = [["eventSource"],[service+".amazonaws.com"]]
        # return "{} {} {} {} {} {} {} {}".format(type, user_name, time1, time2, event_name, request_parameters[0], request_parameters[1], count)

    else:
        return json.dumps("Error")

    return action(type, user_name=user_name, time1=time1, time2=time2, event_name=event_name, request_parameters=request_parameters, count=count)

def action(type, user_name=None, time1=None, time2=None, event_name=None, request_parameters=None, count=False):

    if type == "actions_between":
        return json.dumps(Querys.actions_between_time(
            time1,
            time2,
            event=event_name,
            request_parameter=request_parameters,
            count=count
        ))
    elif type == "used_services":
        return json.dumps(
            Querys.used_services(user_name, time1, time2, count)

        )

    elif type == "used_services_parameter":
        return json.dumps(
            Querys.used_services_parameter(
                user_name, request_parameters, time1, time2, count
            )

        )

    elif type == "user_count_event":
        return json.dumps((
            Querys.user_count_event(user_name, event_name, time1, time2, request_parameters, count)

        ))

    elif type == "top_users":
        return json.dumps(
            Querys.top_users(time1, time2, event_name, request_parameters)
        )

    elif type == "users_list":
        return json.dumps(Querys.users_list())



    return "Error: {}".format(event.keys())


if __name__ == '__main__':
    event = {
    "user":  "alucloud171",
    "count":  "",
    "eventName":  "",
    "from":  "",
    "to":  "",
    "param":  "",
    "value":  ""
    }
    res = handler(event, None)
    print(res)