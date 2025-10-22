import json
import time
from datetime import datetime, timezone
from random import randint
from paho.mqtt import client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "demo"
QOS = 0


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Connected to {BROKER}:{PORT}")
        client.subscribe(TOPIC, qos=QOS)
        print(f"Subscribed to: {TOPIC}")
    else:
        print(f"Connect failed with code {rc}")


def on_message(client, userdata, msg):
    print(f"\nRecieved from topic={msg.topic}, qos={msg.qos}")
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        dev = data.get("DeviceName")
        temp = data.get("temperature")
        hum = data.get("humidity")
        print(f"  DeviceName : {dev}")
        print(f"  temperature: {temp}")
        print(f"  humidity   : {hum}")
    except json.JSONDecodeError:
        print(f"  Error: {msg.payload!r}")


def publish(client):
    payload = {
        "DeviceName": "from-py",
        "temperature": 20,
        "humidity": 60
    }
    info = client.publish(TOPIC, payload=json.dumps(payload), qos=QOS, retain=False)
    # info.wait_for_publish()
    print(f"Publishing {payload}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    try:
        publish(client)
        client.loop_forever()
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
