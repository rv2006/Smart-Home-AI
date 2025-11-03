import paho.mqtt.client as mqtt
import time
import random
import datetime # Used to get the real hour

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = f"hardware-simulator-client-{random.randint(0, 1000)}"

def on_message(client, userdata, msg):
    print(f"--- COMMAND RECEIVED ---")
    print(f"Topic: {msg.topic} | Payload: {msg.payload.decode('utf-8')}")
    print(f"------------------------")

client = mqtt.Client(client_id=CLIENT_ID)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883)

# Subscribe to all control topics
client.subscribe("myhome/control/#")
client.loop_start() 
print(f"Hardware Simulator ({CLIENT_ID}) is RUNNING. Publishing sensor data...")

try:
    while True:
        # --- Simulate Data ---
        sim_temp = round(random.uniform(20.0, 32.0), 2)
        sim_light = random.randint(10, 1000)
        sim_motion = random.choice(["NONE", "DETECTED"])
        
        # --- Get Real Hour ---
        # This makes the "hour_of_day" feature meaningful
        current_hour = datetime.datetime.now().hour

        # --- Publish Data ---
        client.publish("myhome/sensors/temperature", str(sim_temp))
        client.publish("myhome/sensors/light", str(sim_light))
        client.publish("myhome/sensors/motion", sim_motion)
        # We don't need to send the hour, the app.py will get it itself.
        
        print(f"Data Published: (Hour: {current_hour}) Temp={sim_temp}, Light={sim_light}, Motion={sim_motion}")
        time.sleep(5) 

except KeyboardInterrupt:
    print("Stopping hardware simulator...")
    client.loop_stop()
    client.disconnect()