import json,requests, ast, csv
from operator import attrgetter

API_url = "https://aekot17gqj.execute-api.us-east-1.amazonaws.com/test/alucloud230query"

def save_path(data, path):
    print((data))
    with open(path, 'a') as outcsv:
        # configure writer to write standard csv file
        writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

        writer.writerow(['date', 'number'])
        for item in data:
            # Write item to outcsv
            writer.writerow([item[0], item[1]])



def APiCaller(parameters = {}):
    response = requests.post(API_url, json=parameters)
    #[{"eventTime": "2017-04-09T18:42:11Z", "userIdentity_userName": "alucloud179"}, {"eventTime": "2017-04-09T22:27:58Z", "userIdentity_userName": "alucloud179"}
    return ast.literal_eval(response.json())


def count_events_day(events=[]):
    counter = {}

    #{"eventTime": "2014-09-26T11:34:06Z", "userIdentity_userName": "gmolto"}
    # 10 first characters are the day

    for event in events:

        day = event["eventTime"]
        #user = events["userIdentity_userName"]
        day = day[:10]
        events_number = counter.get(day,0)
        counter[day] = events_number + 1

    event_list = []
    for k in counter.keys():
        event_list.append((k, counter[k]))

    #order list
    sorted_list = sorted(event_list )

    return sorted_list

if (__name__ == '__main__'):


    parameters = {
      "httpMethod": "POST",
      "type": "used_services",
      "count": "False",
      "user": "amcaar",
      "event": "RunInstances",
      "time1": "2013-06-01T12:00:51Z",
      "time2": "2018-06-01T19:00:51Z",
      "request_parameter": [
        "requestParameters_instanceType",
        "m1.small"
      ]
    }
    data = APiCaller(parameters)
    print(data)
    events_per_day = count_events_day(data)
    save_path(events_per_day, "event_days.csv")