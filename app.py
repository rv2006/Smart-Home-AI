import streamlit as st
import paho.mqtt.client as mqtt
import time
import random
import threading
import queue

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = f"edge-ai-dashboard-client-{random.randint(0, 1000)}"

# --- 1. Thread-Safe Queue ---
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = queue.Queue()

# --- 2. Session State for Data ---
# We've added "reason" states to track AI vs Voice commands
if 'data' not in st.session_state:
    st.session_state.data = {
        "temp": "N/A",
        "light": "N/A",
        "motion": "N/A",
        "connected": False,
        "kitchen_state": "OFF",
        "entertainment_state": "OFF",
        "light_state_reason": "AUTO", # Tracks if light is on by AUTO or VOICE
        "hvac_state_reason": "AUTO"   # Tracks if HVAC is on by AUTO or VOICE
    }

# --- 3. MQTT Client Initialization (Unchanged) ---
if 'client' not in st.session_state:
    st.session_state.client = mqtt.Client(client_id=CLIENT_ID)
    print(f"Main App: Created MQTT Client ({CLIENT_ID})")

# --- 4. MQTT Thread Function (Unchanged) ---
def mqtt_thread_worker(data_queue, client):
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Thread: Connected!")
            client.subscribe("myhome/sensors/temperature")
            client.subscribe("myhome/sensors/light")
            client.subscribe("myhome/sensors/motion")
            data_queue.put({"topic": "status", "payload": True})
        else:
            print(f"MQTT Thread: Connection failed, code {rc}")
            data_queue.put({"topic": "status", "payload": False})

    def on_message(client, userdata, msg):
        print(f"MQTT Thread: Data Received: {msg.topic} | {msg.payload.decode('utf-8')}")
        data_queue.put({"topic": msg.topic, "payload": msg.payload.decode('utf-8')})

    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, 1883)
        client.loop_forever() 
    except Exception as e:
        print(f"MQTT Thread Error: {e}")
        data_queue.put({"topic": "status", "payload": False})

# --- 5. Start MQTT Thread (Unchanged) ---
if 'mqtt_thread_started' not in st.session_state:
    print("Main App: Starting MQTT thread...")
    t = threading.Thread(
        target=mqtt_thread_worker, 
        args=(st.session_state.data_queue, st.session_state.client), 
        daemon=True
    )
    t.start()
    st.session_state.mqtt_thread_started = True

# --- 6. Update Data from Queue (Unchanged) ---
while not st.session_state.data_queue.empty():
    msg = st.session_state.data_queue.get()
    
    if msg["topic"] == "status":
        st.session_state.data["connected"] = msg["payload"]
    elif msg["topic"] == "myhome/sensors/temperature":
        st.session_state.data["temp"] = msg["payload"]
    elif msg["topic"] == "myhome/sensors/light":
        st.session_state.data["light"] = msg["payload"]
    elif msg["topic"] == "myhome/sensors/motion":
        st.session_state.data["motion"] = msg["payload"]

# --- 7. Page Layout ---
st.set_page_config(layout="wide")
st.title("🧠 AI Smart Home - Edge Device & Dashboard")

st.sidebar.header("Simulation Status")
if st.session_state.data["connected"]:
    st.sidebar.success("✅ Connected to Broker")
else:
    st.sidebar.error("❌ DISCONNECTED")

st.write("---")
col1, col2 = st.columns(2)

# --- COLUMN 1: Inputs ---
with col1:
    st.header("Inputs (Live Sensor Feed)")
    st.subheader(f"🌡️ Temperature: **{st.session_state.data['temp']} °C**")
    st.subheader(f"☀️ Light Level: **{st.session_state.data['light']}**")
    st.subheader(f"🏃 Motion: **{st.session_state.data['motion']}**")

    st.header("Voice Control (Simulated)")
    voice_command = st.text_input("Enter command:")
    
    # --- *** THIS IS THE NEW, FIXED LOGIC *** ---
    if st.button("Send Voice Command"):
        cmd = voice_command.lower()
        found_command = False

        # Reset any voice overrides to AUTO
        st.session_state.data["light_state_reason"] = "AUTO"
        st.session_state.data["hvac_state_reason"] = "AUTO"
        
        # --- Check for Kitchen ---
        if "kitchen" in cmd:
            if "on" in cmd:
                st.session_state.data["kitchen_state"] = "ON"
                st.session_state.client.publish("myhome/control/kitchen", "ON")
                found_command = True
            elif "off" in cmd:
                st.session_state.data["kitchen_state"] = "OFF"
                st.session_state.client.publish("myhome/control/kitchen", "OFF")
                found_command = True
        
        # --- Check for Entertainment (Independent 'if') ---
        if "entertainment" in cmd:
            if "on" in cmd:
                st.session_state.data["entertainment_state"] = "ON"
                st.session_state.client.publish("myhome/control/entertainment", "ON")
                found_command = True
            elif "off" in cmd:
                st.session_state.data["entertainment_state"] = "OFF"
                st.session_state.client.publish("myhome/control/entertainment", "OFF")
                found_command = True
        
        # --- Check for Lighting (Independent 'if') ---
        if "light" in cmd or "lighting" in cmd:
            if "on" in cmd:
                st.session_state.data["light_state_reason"] = "VOICE"
                st.session_state.client.publish("myhome/control/light", "ON")
                found_command = True
            elif "off" in cmd:
                st.session_state.data["light_state_reason"] = "VOICE"
                st.session_state.client.publish("myhome/control/light", "OFF")
                found_command = True

        # --- Check for HVAC (Independent 'if') ---
        if "hvac" in cmd or "air" in cmd or "cooling" in cmd:
            if "on" in cmd:
                st.session_state.data["hvac_state_reason"] = "VOICE"
                st.session_state.client.publish("myhome/control/hvac", "ON")
                found_command = True
            elif "off" in cmd:
                st.session_state.data["hvac_state_reason"] = "VOICE"
                st.session_state.client.publish("myhome/control/hvac", "OFF")
                found_command = True

        if not found_command:
            st.warning("Voice command not recognized.")

# --- COLUMN 2: Outputs (AI Decisions) ---
with col2:
    st.header("Outputs (Appliance Control)")
    try:
        temp = float(st.session_state.data['temp'])
        light = int(st.session_state.data['light'])
        motion = st.session_state.data['motion']
    except (ValueError, TypeError):
        temp, light, motion = 25, 500, "NONE"

    # --- AI Model: Automatic + Voice Logic ---
    st.subheader("❄️ HVAC System")
    if st.session_state.data["hvac_state_reason"] == "VOICE":
        st.error(f"Status: **ON** (Reason: Voice Command)")
    elif temp > 28.0:
        st.error(f"Status: **ON (COOLING)** (Reason: Auto - Temp is {temp}°C)")
    else:
        st.success(f"Status: **OFF** (Reason: Auto - Temp is {temp}°C)")

    st.subheader("💡 Lighting System")
    if st.session_state.data["light_state_reason"] == "VOICE":
        st.error(f"Status: **ON** (Reason: Voice Command)")
    elif motion == "DETECTED" and light < 400:
        st.error(f"Status: **ON** (Reason: Auto - Motion {motion}, Light {light})")
    else:
        st.success(f"Status: **OFF** (Reason: Auto - Motion {motion}, Light {light})")

    st.subheader("🍳 Kitchen Appliances")
    if st.session_state.data["kitchen_state"] == "ON":
        st.error("Status: **ON** (Reason: Voice Command)")
    else:
        st.success("Status: **OFF**")
        
    st.subheader("📺 Entertainment Devices")
    if st.session_state.data["entertainment_state"] == "ON":
        st.error("Status: **ON** (Reason: Voice Command)")
    else:
        st.success("Status: **OFF**")

# --- 8. Auto-Refresh Loop ---
time.sleep(1)
st.rerun()