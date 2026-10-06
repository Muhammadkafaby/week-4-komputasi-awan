import json
import os
import random
import time

import paho.mqtt.client as mqtt

BROKER = os.getenv("MQTT_BROKER", "mosquitto")
INTERVAL = int(os.getenv("INTERVAL", "60"))
TOPIC = "sensor/dummy"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, 1883, 60)
client.loop_start()

print(f"Publisher kirim data sensor dummy tiap {INTERVAL} detik ke topik '{TOPIC}'", flush=True)
while True:
    data = {
        "suhu": round(random.uniform(25, 35), 2),
        "kelembapan": round(random.uniform(40, 80), 2),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(TOPIC, json.dumps(data))
    print("kirim:", data, flush=True)
    time.sleep(INTERVAL)
