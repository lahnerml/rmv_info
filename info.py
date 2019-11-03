import datetime
import json
import pytz
import time
import urllib

# Customization:
# RMV API token
from access_token import token

# Station ID of Origin
from origin import depart_station

# Elements of RMV query
request = {"accessId": token,
           "id": depart_station.station_id,
           "products": "class05",
           "format": "json",
           }


def perform_query():
    req = urllib.parse.urlencode(request)
    site = "https://www.rmv.de/hapi/departureBoard?" + req
    reply = json.loads(urllib.request.urlopen(site).read())
    return reply


def extract_mean_of_transportation(reply):
    reply_data = reply["Departure"]
    reply_sbahn = list(filter(lambda x: x["trainCategory"] == "SBU",
                              reply_data))
    sbahn_right_direction = list(filter(lambda x: x["track"] == "2",
                                        reply_sbahn))
    return sbahn_right_direction


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
    print(result["time"].strftime("%H:%M:%S"))
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
        relevant_connections = extract_mean_of_transportation(reply)

    result = calculate_time_diffs(relevant_connections)

    display_result(result)

    ctr += sleep_sec
    ctr %= query_every_sec
    time.sleep(sleep_sec)
