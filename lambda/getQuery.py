from __future__ import print_function
import boto3
import os
import sys
import uuid, json
from DynamoDB import Querys
# import requests

"""YYYY-MM-DD to YYYY-MM-DDTHH-MM-SSZ only when its necessary """
def format_time(time):
    if(not time): return None
    if len(time) == 10:
        time = time + "T00:00:00Z"

    if len(time) != 20:
        raise Exception("Error on time format!")

    return time


# {
    #     "httpMethod": "GET",
    #     "type": "actions_between",
    #     "event": "RunInstances",
    #     "time1": "2014-06-01",
    #     "time2": "2018-06-01",
    #     "request_parameter": [
    #         "requestParameters_instanceType",
    #         "m1.small"
    #     ]
    # }
def handler(event, context):

    if event.get("list_users", None):
        return action("users_list")

    # type = event.get("type",None)
    request = event.get("param",None)
    parameter = event.get("value",None)
    if request and parameter :
        request_parameters = [request, parameter]
    else:
        request_parameters = None

    event_name = event.get("eventName",None)
    user_name = event.get("user",None)
    service = event.get("service",None)
    count = event.get("count",True)

    time1 = format_time(event.get("from",None))
    time2 = format_time(event.get("to",None))

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
        "httpMethod": "GET",
        "type": "used_services",
        "user": "gmolto",
        "event": "RunInstances",
        "time1": "2014-06-01",
        "time2": "2018-06-01",
        "request_parameter": [
            "requestParameters_instanceType",
            "m1.small"
        ]
    }
    res = handler(event, None)
    print(res)