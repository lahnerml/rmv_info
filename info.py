import datetime
import json
import pytz
import urllib
from access_token import token


class Station:
    def __init__(self, name, sid):
        self.station = name
        self.station_id = sid


ES = Station("Eschborn Südbahnhof", 3002299)

request = {"accessId": token,
           "id": ES.station_id,
           "products": "class05",
           "format": "json",
           }

req = urllib.parse.urlencode(request)
site = "https://www.rmv.de/hapi/departureBoard?" + req
print(site)

raw_reply = urllib.request.urlopen(site)
reply = json.loads(raw_reply.read())

reply_data = reply["Departure"]
reply_sbahn = list(filter(lambda x: x["trainCategory"] == "SBU", reply_data))
sbahn_fbound = list(filter(lambda x: x["track"] == "2", reply_sbahn))

dt_now = datetime.datetime.now(tz=pytz.timezone("Europe/Berlin"))

print(dt_now.strftime("%H:%M:%S"))
for trains in sbahn_fbound:
    depart = datetime.datetime.strptime(trains["rtTime"], "%H:%M:%S")
    depart = depart.replace(year=dt_now.year, month=dt_now.month,
                            day=dt_now.day,
                            tzinfo=pytz.timezone("Europe/Berlin"))
    print(trains["name"], trains["rtTime"], depart- dt_now)
