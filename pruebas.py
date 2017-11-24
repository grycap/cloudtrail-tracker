from ast import literal_eval
import settings

f = open("analysis_events", "r")
lines = f.readlines()

total = 0
total_gets = 0
total_decrypt = 0
rest = 0

for line in lines:
    t = literal_eval(line)

    total += t[0]

    if t[1].lower().startswith(tuple(settings.filterEventNames[:-1])):
        total_gets += t[0]
    elif t[1].lower().startswith("decrypt"):
        total_decrypt += t[0]
    else:
        rest += t[0]

print("Total events %d " % total)
print("Total of get events %d - %f %%" % (total_gets, total_gets/total))
print("Total of decrypt events %d - %f %%" % (total_decrypt, total_decrypt/total))
print("rest of events %d - %f %%" % (rest, rest/total))