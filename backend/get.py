import requests

READ_URL = "https://api.thingspeak.com/channels/3116996/feeds.json"
params = {"results": 2}
r = requests.get(READ_URL, params=params)

if r.status_code == 200:
    feeds = r.json()
    print("Recent feeds:", feeds["feeds"][1])
else:
    print("Error reading data:", r.status_code)
