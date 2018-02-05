from __future__ import print_function
import boto3
import os
import sys
import uuid, json
from DynamoDB import Querys
# import requests

"""YYYY-MM-DD to YYYY-MM-DDTHH-MM-SSZ only when its necessary """
def format_time(time):
    if(time is None): return None
    if len(time) == 10:
        time = time + "T00:00:00Z"

    if len(time) != 20:
        raise Exception("Error on time format!")

    return time

def handler(event, context):
    # data = json.loads(event)
    type = event.get("type",None)
    # {
    #     "httpMethod": "GET",
    #     "type": "actions_between",
    #     "event": "RunInstances",
    #     "time1": "2014-06-01T12:00:51Z",
    #     "time2": "2018-06-01T19:00:51Z",
    #     "request_parameter": [
    #         "requestParameters_instanceType",
    #         "m1.small"
    #     ]
    # }
    request = event.get("request",None)
    parameter = event.get("parameter",None)
    if request and parameter :
        request_parameters = [request, parameter]
    else:
        request_parameters = None

    event_name = event.get("event",None)
    user_name = event.get("user",None)
    count = event.get("count",True)
    if count == "False": count = False
    time1 = format_time(event.get("time1"))
    time2 = format_time(event.get("time2"))

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
        "time1": "2014-06-01T12:00:51Z",
        "time2": "2018-06-01T19:00:51Z",
        "request_parameter": [
            "requestParameters_instanceType",
            "m1.small"
        ]
    }
    res = handler(event, None)
    print(res)