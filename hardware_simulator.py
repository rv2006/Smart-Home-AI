import paho.mqtt.client as mqtt
import time
import random

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "hardware-simulator-client"

# This runs when a command is SENT BACK from the AI
def on_message(client, userdata, msg):
    print(f"--- COMMAND RECEIVED ---")
    print(f"Topic: {msg.topic} | Payload: {msg.payload.decode('utf-8')}")
    print(f"------------------------")

# --- Setup ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883)

# Subscribe to the control topics to listen for commands
client.subscribe("myhome/control/light")
client.subscribe("myhome/control/hvac")

client.loop_start() # Starts a background thread to listen for messages
print("Hardware Simulator is RUNNING. Publishing sensor data...")

try:
    while True:
        # --- 1. Simulate Sensor Data ---
        sim_temp = round(random.uniform(20.0, 30.0), 2)
        sim_light = random.randint(100, 1000)
        sim_motion = random.choice(["NONE", "DETECTED"])

        # --- 2. Publish Data to the "Brain" ---
        client.publish("myhome/sensors/temperature", str(sim_temp))
        client.publish("myhome/sensors/light", str(sim_light))
        client.publish("myhome/sensors/motion", sim_motion)
        
        print(f"Data Published: Temp={sim_temp} C, Light={sim_light}, Motion={sim_motion}")
        
        # Wait 5 seconds before sending new data
        time.sleep(5) 

except KeyboardInterrupt:
    print("Stopping hardware simulator...")
    client.loop_stop()
    client.disconnect()