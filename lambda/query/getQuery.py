# CloudTrail-Tracker
# Copyright (C) GRyCAP - I3M - UPV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function
import boto3
import os
import sys, ast
import uuid, json, time, datetime
try:
    from dynamodb import Querys
except Exception as e:
    sys.path.insert(1, os.path.join(sys.path[0], '../..')) # just to run on local
    from dynamodb import Querys
# import requests

def format_time(time):
    """YYYY-MM-DD to YYYY-MM-DDTHH-MM-SSZ only when its necessary """
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
    """
    Makes a list with param and value preparing to query
    :param event:
    :return: list: [[requests], [parameters]]. requqest and parameters are list of String. len(requests) == len(parameters)
    """
    request = event.get("param", None)
    parameter = event.get("value", None)
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

def add_time(t, seconds=1):
    """
    Add days
    :param t:
    :param days:
    :return:
    """
    print(t)
    print(type(t))
    if type(t) == str:
        t = datetime.datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

    time1 = t + datetime.timedelta(seconds=seconds)

    return time1

def handler(event, context):
    """
    Handler for Lambda function
    :param event: dict from Lambda
    :param context:
    :return: result. Depends on API Gateway
    """

    if event.get("list_users", None):
        return action("users_list")
    if event.get("services_list", None):
        return action("services_list")
    if event.get("parameters_list", None):
        return action("parameters_list")
    scan = event.get("scan", None)

    request_parameters = get_request_parameters(event)

    event_name = event.get("eventName",None)
    user_name = event.get("user",None)
    service = event.get("service",None)
    count = event.get("count",False)
    time1 = event.get("from",None)
    time2 = event.get("to",None)
    begin_with = event.get("begin_with",None)

    if not count or count == "false" or count == "False":
        count = False
    if not begin_with or begin_with == "false" or begin_with == "False":
        begin_with = False
    if not event_name: #necessary if eventName is "" or False
        event_name = None
    if not service:
        service = None
    if not time1:
        time1 = time.strftime("%Y-%m-%d")
        date_1 = datetime.datetime.strptime(time1, "%Y-%m-%d")
        time1 = date_1 - datetime.timedelta(days=7)
        time1 = time1.strftime("%Y-%m-%d")
    if not time2:
        time2 = time.strftime("%Y-%m-%d")


    time1 = format_time(time1)
    time2 = format_time(time2)
    time2 = add_time(time2)
    #Select action
    if scan:
        method = "actions_between"
    elif user_name and not service:
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
        return ("Error. Needed an user name or a service.")

    return action(method, user_name=user_name, time1=time1, time2=time2, event_name=event_name, request_parameters=request_parameters, count=count, begin_with=begin_with)

def action(method, user_name=None, time1=None, time2=None, event_name=None, request_parameters=None, count=False, begin_with=False):
    """
    Call to Query and return the result from DynamoDB
    :param method: String. Name of the function of Query.py
    :param user_name: String
    :param time1: String. Y-%m-%dT%H:%M:%SZ or Y-%m-%dT
    :param time2: String. Y-%m-%dT%H:%M:%SZ or Y-%m-%dT
    :param event_name: String
    :param request_parameters: list. see method get_request_parameters
    :param count: boolean
    :param begin_with: boolean
    :return: list of dict or number, on depends of count.
    """
    if method == "actions_between":
        return (Querys.actions_between_time(
            time1,
            time2,
            event=event_name,
            request_parameter=request_parameters,
            count=count,
            begin_with=begin_with
        ))
    elif method == "used_services":

        return (
            Querys.used_services(user_name, time1, time2, count)

        )

    elif method == "used_services_parameter":
        return (
            Querys.used_services_parameter(
                user_name, request_parameters, time1, time2, count
            )

        )

    elif method == "user_count_event":
        return ((
            Querys.user_count_event(user_name, event_name, time1, time2, request_parameters, count, begin_with=begin_with)

        ))

    elif method == "top_users":
        return (
            Querys.top_users(time1, time2, event_name, request_parameters,  begin_with=begin_with)
        )

    elif method == "users_list":
        return (Querys.users_list())
    elif method == "services_list":
        return (Querys.services_list())
    elif method == "parameters_list":
        return (Querys.parameters_list())



    return "Error: {}".format(event.keys())


if __name__ == '__main__':
    event = {
    # "user":  "alucloud178",
    "service": "",
    "scan": "True",
    "count":  "",
    "eventName":  "CreateDBInstance",
    "from":  "2014-06-01T12:00:51Z",
    "to":  "2017-09-01",
    "count": True,
    "begin_with": True,
    # "param":  "['instanceType']",
    # "param":  "instanceType,eventSource",
    # "value":  "['m1.small']"
    # "value":  "m1.small,ec2.amazonaws.com"
    }
    res = handler(event, None)
    print(res)