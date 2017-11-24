import boto3
import os, time, argparse
from Write import UseDynamoDB
from my_parser import Event
import Querys
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="Path that contains items to start the analysis", default='./examples')
parser.add_argument("--porc_chunk", help="Split the data. 0.1 = splits of 10%. Default 0.1", default=0.1)
parser.add_argument("--upload", help="Upload files", default=False)

def chunks(l, porc=0.1):
    """Yield successive n-sized chunks from l."""
    print(int(len(l)))
    percent = max(1,int(len(l) * porc))
    print(percent)
    for i in range(0, len(l)+1, percent):
        if i + percent+1 >= len(l):
            yield l[i : ]
            return;
        else:
            yield l[i : i + percent]
        #last = i

def get_structure(path):
    res = []
    for (path,i,j) in os.walk(path):
        # print(path)
        # print(j)
        if len(j) > 0:
            aux = [os.path.join(path,x) for x in j]
            res.extend(aux)
    return res


"""6 querys call"""
def querys(times_chunk):


    start_time = time.time()
    user_events = Querys.user_count_event('gmolto', 'DescribeMetricFilters', '2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for user_count_event items %f " % elapsed_time)
    times_chunk[2] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.used_services('alucloud171', '2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for used_services items %f " % elapsed_time)
    times_chunk[3] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.users_list()
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for users_list items %f " % elapsed_time)
    times_chunk[4] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.top_users('2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for top_users items %f " % elapsed_time)
    times_chunk[5] = (elapsed_time)


    start_time = time.time()
    user_events = Querys.actions_between_time('2016-06-01T12:00:51Z', '2018-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for  actions_between_time (all events) %f " % elapsed_time)
    times_chunk[6] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.actions_between_time('2016-06-01T12:00:51Z', '2018-06-01T19:00:51Z', event='DescribeInstanceStatus')
    elapsed_time = time.time() - start_time
    # print(user_events)
    print("      ---- > Time elapsed for  actions_between_time (one event) %f " % elapsed_time)
    times_chunk[7] = (elapsed_time)

def save_array(data, path):

    with open(path, 'a') as outfile:
        outfile.write('#\n')
        for data_slice in data:
            [outfile.write(str(x)+" ") for x in data_slice]
            outfile.write('\n')

""" Save events from a dir ans calculate times"""
def analysis_upload_query(path, porc_chunk = 0.1, table_name = 'EventoCloudTrail_V2'):
    #Get all events from path

    print("Path of files: %s with %d files" % (path, len(path)))
    events = get_structure(path)
    #split in equal parts (except last)
    #matrix for saves times
    save_times = []
    number_events = 0
    for l in chunks(events, porc_chunk):
        time_chunk = [None]*9
        #All times for chunck,
        #[NUMBER_EVENTS, T_Upload, user_events, user_events_service, user_list, top_users, act_between,times,
        #act_between_times_events, ALL]
        print("Uploading %d files " % len(l))
        start_time = time.time()
        count = 0
        for e in l: #e = events file
            count = count + 1
            event = Event(e)
            print(" -------------------------File Number %d with %d events " % (count, event.count_events()))
            number_events = number_events + event.count_events()
            db = UseDynamoDB("prueba", verbose=False)
            db.guardar_evento(table_name, event)
        elapsed_time_upload = time.time() - start_time
        time_chunk[0] = number_events
        time_chunk[1] = elapsed_time_upload
        print("Time elapsed for upload %d events: %f " % (number_events, elapsed_time_upload))
        print(" - Calculating time for querys.. ")

        dinosaurs_time = time.time()
        try:
            querys(time_chunk)
        except Exception:
            print("Too many time, more read capacity is required!")
        elapsed_time_dinosaurs = time.time() - dinosaurs_time
        print("Time elapsed for all querys (%d number of items): %f " % (number_events, elapsed_time_dinosaurs))

        print(" -  Querys finished.. ")
        time_chunk[8] = (elapsed_time_dinosaurs)
        save_times.append(time_chunk)

    print("Saving array of times...")
    save_array(save_times, 'times/times')

"""Upload all files from path.
Do a tracing with a file history and starts from the last point"""
def upload_all(path, table_name = 'EventoCloudTrail_V2'):
    # Get all events from path
    path_tracing  = "tracing_items"
    print("Path of files: %s with " % (path))

    if not os.path.exists(os.path.join(path_tracing)):
        f = open(path_tracing, "w")
        f.close()

    file_trace = open(path_tracing, "r")

    traced_items = file_trace.readlines()
    traced_items = [x[:-1] for x in traced_items]
    file_trace.close()
    print("Traced files: %d" % (len(traced_items)))
    events = get_structure(path)

    print("Number of files: %d" % len(events))
    events = list(set(events) - set(traced_items))
    print("Number of total files to upload: %d" % len(events))

    file_trace = open(path_tracing, "a+")
    for e in events:  # e = events file
        event = Event(e)
        db = UseDynamoDB("Uploading", verbose=False)
        db.guardar_evento(table_name, event)
        file_trace.write(e+"\n")
        file_trace.flush()


    file_trace.close()

def query_analyze():
    # TODO only analyze
    pass

def count_logs(path, words):
    events = get_structure(path)
    # print(events)
    num_events = 0
    num_events_word = 0
    for ev in events:  # e = events file
        event = Event(ev)
        for e in event.events():
            num_events += 1

            # print(e)
            name_event = e.get("eventName", None)
            # print(name_event)

            if name_event is None or name_event.lower().startswith(tuple(words)):
                num_events_word += 1
    print("Total number of events: %d " % num_events)
    print("number of events with the words %s: %d , %f" % (words, num_events_word, num_events_word/num_events))

def count_eventNames(path):
    events = get_structure(path)
    # print(events)
    num_events = 0
    res = {}
    eventsID = {}
    collision = {}
    for ev in events:  # e = events file
        event = Event(ev)
        for e in event.events():
            num_events += 1

            # print(e)
            id = e.get("eventID", None)
            numEventID = eventsID.get(id, 0)
            eventsID[id] = numEventID + 1
            if (numEventID + 1 > 1):
                #repeated - collision!
                collision[id] = numEventID + 1

            name_event = e.get("eventName", None)
            # print(name_event)
            n = res.get(name_event, 0)
            res[name_event] = n+1



    arr = []
    for k in res:
        arr.append((res[k],k, res[k]/num_events))
    arr.sort()
    for a in arr:
        print(a)
    print(collision)
    print("Total number of events: %d " % num_events)
    print("Total number of REPEATED events: %d " % len(collision.keys()))

def main():
    args = parser.parse_args()
    path = args.path
    porc_chunk = float(args.porc_chunk)

    # analysis_upload_query(path, porc_chunk)
    args.upload = False
    if args.upload:
        upload_all(path, table_name="EventoCloudTrail_230_less")
    # upload_all(path,table_name="EventoCloudTrail_230_less")
    words = ["get","describe", "list", "info", "decrypt"]
    count_eventNames(path)

if (__name__ == '__main__'):
    main()