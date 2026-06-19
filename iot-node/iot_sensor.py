import time
import random
import json
import paho.mqtt.client as mqtt

#GCP_BROKER_IP = "<BROKER_IP>" # Set your MQTT broker IP here
MQTT_PORT = 1883
#MQTT_TOPIC = "<TOPIC>" # Set your MQTT topic here

print("]------ IoT Device Emulation (VLAN 20) Started -------[")

client = mqtt.Client()
#client.username_pw_set("<USERNAME>", "<PASSWORD>") # Uncomment and set if authentication is required

try:
    client.connect(GCP_BROKER_IP, MQTT_PORT, 60)
except Exception as e:
    print(f"Cant Connect to broker: {e}")
    exit(1)

while True:
    # random temperature and moisture
    temperature = round(random.uniform(24.5, 32.0), 2)
    humidity = round(random.uniform(50.0, 70.0), 2)

    # make a json
    payload = {
        "device_id": "simulated_node_01",
        "vlan": 20,
        "temperature": temperature,
        "humidity": humidity,
        "status": "ONLINE"
    }

    # convert to string and publish to cloud
    json_data = json.dumps(payload)
    client.publish(MQTT_TOPIC, json_data)

    print(f"success -> Topic: {MQTT_TOPIC} | Data: {json_data}")

    time.sleep(5)