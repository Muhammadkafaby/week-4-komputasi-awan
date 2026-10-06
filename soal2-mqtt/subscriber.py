import os

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
TOPIC = "sensor/dummy"


def on_connect(client, userdata, flags, rc, props=None):
    print(f"Subscriber terhubung ke broker {BROKER}, subscribe '{TOPIC}'", flush=True)
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    print(f"terima [{msg.topic}] {msg.payload.decode()}", flush=True)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_forever()
