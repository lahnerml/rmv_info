import datetime
import json
import pytz
import time
from urllib import parse, request

# Customization:
# RMV API token
from access_token import token

# Station ID of Origin and destionation
from route import origin, destination

# Elements of RMV query
rmv_request = [{"accessId": token,
                "id": origin[0].station_id,
                "direction": destination[0].station_id,
                "duration": 90,
                "format": "json",
                },
               {"accessId": token,
                "id": origin[1].station_id,
                "direction": destination[1].station_id,
                "duration": 150,
                "format": "json",
                }]


# Query data from RMV
def perform_query():
    req = [parse.urlencode(rmv_req) for rmv_req in rmv_request]
    site = ["https://www.rmv.de/hapi/departureBoard?" + r for r in req]
    reply = [json.loads(request.urlopen(s).read()) for s in site]
    return reply


# Calculate time difference and extract relevant infos
def calculate_time_diffs(relevant_connections):
    dt_now = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))
    result = {"time": dt_now, "connections": []}
    for conn in relevant_connections:
        depart = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))
        if "rtTime" in conn:
            dep = datetime.datetime.strptime(conn["rtTime"], "%H:%M:%S")
            t = conn["rtTime"]
        else:
            dep = datetime.datetime.strptime(conn["time"], "%H:%M:%S")
            t = conn["time"] + "*"
        depart = depart.replace(hour=dep.hour,
                                minute=dep.minute,
                                second=dep.second)
        conn_info = {"line": conn["name"],
                     "depart": t,
                     "scheduled": conn["time"],
                     "time_remaining": depart-dt_now}
        result["connections"].append(conn_info)

    return result


# Print results to screen
def display_result(origin, destination, result, next_query):
    print("Connections from {} to {} at {}: \t(next query: {} seconds)"
          .format(origin.name, destination.name,
                  result["time"].strftime("%H:%M:%S"), next_query))
    for c in result["connections"]:
        print("{}\t{}\t(scheduled {})\t{} remaining".format(
            c["line"], c["depart"], c["scheduled"], str(c["time_remaining"])))


ctr = 0
sleep_sec = 1
query_every_sec = 90
while(True):
    if 0 == ctr % query_every_sec:
        reply = perform_query()

    for i in range(len(reply)):
        result = calculate_time_diffs(reply[i]["Departure"])

        display_result(origin[i], destination[i], result, query_every_sec - ctr)

    ctr += sleep_sec
    ctr %= query_every_sec
    time.sleep(sleep_sec)
