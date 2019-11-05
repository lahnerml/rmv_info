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
rmv_request = {"accessId": token,
               "id": origin.station_id,
               "direction": destination.station_id,
               "format": "json",
               }


# Query data from RMV
def perform_query():
    req = parse.urlencode(rmv_request)
    site = "https://www.rmv.de/hapi/departureBoard?" + req
    reply = json.loads(request.urlopen(site).read())
    return reply["Departure"]


# Calculate time difference and extract relevant infos
def calculate_time_diffs(relevant_connections):
    dt_now = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))
    result = {"time": dt_now, "connections": []}
    for conn in relevant_connections:
        depart = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))
        dep = datetime.datetime.strptime(conn["rtTime"], "%H:%M:%S")
        depart = depart.replace(hour=dep.hour,
                                minute=dep.minute,
                                second=dep.second)
        conn_info = {"line": conn["name"],
                     "depart": conn["rtTime"],
                     "scheduled": conn["time"],
                     "time_remaining": depart-dt_now}
        result["connections"].append(conn_info)

    return result


# Print results to screen
def display_result(result, next_query):
    print("Connections from {} to {} at {}: ({} seconds until next query)"
          .format(origin.name, destination.name,
                  result["time"].strftime("%H:%M:%S"), next_query))
    for c in result["connections"]:
        print("{}\t{}, (scheduled {})\t{} remaining".format(
            c["line"], c["depart"], c["scheduled"], str(c["time_remaining"])))


ctr = 0
sleep_sec = 1
query_every_sec = 90
while(True):
    if 0 == ctr % query_every_sec:
        reply = perform_query()

    result = calculate_time_diffs(reply)

    display_result(result, query_every_sec - ctr)

    ctr += sleep_sec
    ctr %= query_every_sec
    time.sleep(sleep_sec)
