import requests

API_KEY = "3XCZKLV99CT48SWT"
URL = "https://api.thingspeak.com/update"

# Data
field1 = 20
field2 = 33

# Send GET request
params = {
    "api_key": API_KEY,
    "field1": 1,
    "field2": 2

}
response = requests.post(URL, params=params)

if response.status_code == 200:
    print("✅ Data sent successfully. Entry ID:", response.text)
else:

    print("❌ Failed to send data. Status code:", response.status_code)
