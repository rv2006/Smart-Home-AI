import paho.mqtt.client as mqtt
import time
import random
import datetime

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = f"hardware-simulator-client-{random.randint(0, 1000)}"

def on_message(client, userdata, msg):
    print(f"--- COMMAND RECEIVED ---")
    print(f"Topic: {msg.topic} | Payload: {msg.payload.decode('utf-8')}")
    print(f"------------------------")

# --- This is the new "Smart" logic ---
def get_smart_sensor_data():
    """Generates realistic sensor data based on the hour of the day."""
    hour = datetime.datetime.now().hour
    
    # Default values
    temp_base = 25
    light_base = 400
    motion_chance = 0.2 # 20% chance of motion
    
    if 0 <= hour < 6: # Deep Night (0:00 - 5:59)
        temp_base = 22
        light_base = 10
        motion_chance = 0.1
    elif 6 <= hour < 9: # Morning (6:00 - 8:59)
        temp_base = 24
        light_base = 300
        motion_chance = 0.7 # High motion
    elif 9 <= hour < 12: # Mid-day (9:00 - 11:59)
        temp_base = 28
        light_base = 800
        motion_chance = 0.1
    elif 12 <= hour < 16: # Afternoon (12:00 - 15:59)
        temp_base = 32 # Hottest part of the day
        light_base = 1000
        motion_chance = 0.3
    elif 16 <= hour < 19: # Evening (16:00 - 18:59)
        temp_base = 29
        light_base = 350 # Sun is setting
        motion_chance = 0.6
    elif 19 <= hour < 24: # Night (19:00 - 23:59)
        temp_base = 26
        light_base = 40 # Dark
        motion_chance = 0.8 # High motion
        
    # Add randomness to the base values
    sim_temp = round(temp_base + random.uniform(-1.5, 1.5), 2)
    sim_light = light_base + random.randint(-20, 20)
    sim_motion = "DETECTED" if random.random() < motion_chance else "NONE"
    
    return sim_temp, sim_light, sim_motion, hour

# --- Setup MQTT ---
client = mqtt.Client(client_id=CLIENT_ID)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883)
client.subscribe("myhome/control/#")
client.loop_start() 
print(f"Smart Hardware Simulator ({CLIENT_ID}) is RUNNING...")
print("Publishing realistic 24-hour data patterns.")

try:
    while True:
        # Get the new "smart" data
        temp, light, motion, hour = get_smart_sensor_data()

        # Publish Data
        client.publish("myhome/sensors/temperature", str(temp))
        client.publish("myhome/sensors/light", str(light))
        client.publish("myhome/sensors/motion", motion)
        
        print(f"[Hour: {hour:02d}:00] Data Published: Temp={temp}°C, Light={light}, Motion={motion}")
        time.sleep(5) # You can make this faster (e.g., 2s) for testing

except KeyboardInterrupt:
    print("Stopping hardware simulator...")
    client.loop_stop()
    client.disconnect()