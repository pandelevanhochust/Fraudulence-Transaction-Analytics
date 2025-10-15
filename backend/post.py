import requests

API_KEY = "3XCZKLV99CT48SWT"
URL = "https://api.thingspeak.com/update"
CHANNEL_ID = "3116996"
READ_URL  = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
results = 10


field1 = 50
field2 = 100

get_params = {
    "api_key": API_KEY,
    "field1": field1,
    "field2": field2,

}

def write_get():
    print("Gửi theo cách 1:")
    response = requests.get(URL, params=get_params)
    if response.status_code == 200:
        print("Gửi theo cách 1 thành công:", response.text)
    else:
        print("Gửi theo cách 2 không thành công", response.status_code)

post_params = {
    "api_key": API_KEY,
}

body = {
    "field1": field1,
    "field2": field2,
}

def write_post():
    print("Gửi theo cách 2:")
    headers = {"Content-Type": "application/json"}
    response = requests.post(URL, params=post_params,json=body,headers = headers )
    if response.status_code == 200:
        print("Gửi theo cách 2 thành công:", response.text)
    else:
        print("Gửi theo cách 2 không thành công", response.status_code)

def read(n):
    print(f"Lấy {n} bản tin: ")
    r = requests.get(READ_URL, params={"results": n})
    if r.status_code == 200:
        data = r.json()
        feeds = data.get("feeds", [])
        print("Feeds:", feeds)
        for i in feeds:
            print(i)
    else:
        print("Error reading data:", r.status_code)

# write_get()
write_post()
read(1)