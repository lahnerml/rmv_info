import datetime
import json
import pytz
import time
import urllib

# Customization:
# RMV API token
from access_token import token

# Station ID of Origin and destionation
from route import origin, destination

# Elements of RMV query
request = {"accessId": token,
           "id": origin.station_id,
           "direction": destination.station_id,
           "products": "class05",
           "format": "json",
           }


def perform_query():
    req = urllib.parse.urlencode(request)
    site = "https://www.rmv.de/hapi/departureBoard?" + req
    reply = json.loads(urllib.request.urlopen(site).read())
    return reply["Departure"]


def calculate_time_diffs(relevant_connections):
    dt_now = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))
    result = {"time": dt_now, "connections": []}
    for conn in relevant_connections:
        depart = datetime.datetime.strptime(conn["rtTime"], "%H:%M:%S")
        depart = depart.replace(year=dt_now.year, month=dt_now.month,
                                day=dt_now.day,
                                tzinfo=pytz.timezone("Europe/Berlin"))
        conn_info = {"line": conn["name"],
                     "depart": conn["rtTime"],
                     "time_remaining": depart-dt_now}
        result["connections"].append(conn_info)

    return result


def display_result(result):
    print("Connections from {} to {} at {}:".format(
        origin.name, destination.name, result["time"].strftime("%H:%M:%S")))
    for c in result["connections"]:
        print("{}\t{}\t{} remaining".format(c["line"],
                                            c["depart"],
                                            str(c["time_remaining"])))


ctr = 0
sleep_sec = 1
query_every_sec = 90
while(True):
    if 0 == ctr % query_every_sec:
        reply = perform_query()

    result = calculate_time_diffs(reply)

    display_result(result)

    ctr += sleep_sec
    ctr %= query_every_sec
    time.sleep(sleep_sec)
