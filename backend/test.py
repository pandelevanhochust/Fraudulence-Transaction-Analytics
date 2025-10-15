import requests
import json

API_KEY = "T7H40F0X82VGW7L5"
URL = f"https://api.thingspeak.com/update?api_key={API_KEY}"

# JSON data
data = {
    "field1": 20,
    "field2": 33
}

# Send POST request
response = requests.post(URL, json=data)

if response.status_code == 200:
    print("✅ Data sent via JSON successfully. Entry ID:", response.text)
else:
    print("❌ Failed to send JSON data. Status:", response.status_code)
