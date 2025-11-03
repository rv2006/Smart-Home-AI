import streamlit as st
import paho.mqtt.client as mqtt
import time
import random
import threading
import queue
import joblib
import numpy as np
import datetime
import csv
import os

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = f"edge-ai-dashboard-client-{random.randint(0, 1000)}"

# --- 1. Load ML Models ---
try:
    hvac_model = joblib.load('hvac_model.joblib')
    light_model = joblib.load('light_model.joblib')
    motion_encoder = joblib.load('motion_encoder.joblib')
    print("Main App: ML Models loaded successfully.")
except FileNotFoundError:
    st.error("Model files (e.g., hvac_model.joblib) not found! Please run train_model.py first.")
    st.stop() 

# --- 2. Thread-Safe Queue ---
if 'data_queue' not in st.session_state:
    st.session_state.data_queue = queue.Queue()

# --- 3. Session State for Data ---
if 'data' not in st.session_state:
    st.session_state.data = {
        "temp": "N/A", "light": "N/A", "motion": "N/A", "connected": False,
        "kitchen_state": "OFF", "entertainment_state": "OFF",
        
        # --- THIS IS THE KEY ---
        # We track the 'mode' (AUTO or VOICE) and the 'commanded state'
        "light_mode": "AUTO", # Can be "AUTO" or "VOICE"
        "hvac_mode": "AUTO",   # Can be "AUTO" or "VOICE"
        "light_voice_command": "OFF", # Stores the last voice command
        "hvac_voice_command": "OFF"   # Stores the last voice command
    }

# --- 4. MQTT Client Initialization ---
if 'client' not in st.session_state:
    st.session_state.client = mqtt.Client(client_id=CLIENT_ID)
    print(f"Main App: Created MQTT Client ({CLIENT_ID})")

# --- 5. MQTT Thread Function ---
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

# --- 6. Start MQTT Thread ---
if 'mqtt_thread_started' not in st.session_state:
    print("Main App: Starting MQTT thread...")
    t = threading.Thread(
        target=mqtt_thread_worker, 
        args=(st.session_state.data_queue, st.session_state.client), 
        daemon=True
    )
    t.start()
    st.session_state.mqtt_thread_started = True

# --- 7. Update Data from Queue ---
# --- THIS IS THE FIX ---
# This function NO LONGER resets the voice state.
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

# --- 8. Page Layout ---
st.set_page_config(layout="wide")
st.title("🧠 **ML-Powered** Smart Home Dashboard") 

st.sidebar.header("Simulation Status")
if st.session_state.data["connected"]:
    st.sidebar.success("✅ Connected to Broker")
else:
    st.sidebar.error("❌ DISCONNECTED")

current_hour = datetime.datetime.now().hour
st.sidebar.info(f"Current Hour (Feature): **{current_hour}:00**")

st.write("---")
col1, col2 = st.columns(2)

# --- COLUMN 1: Inputs ---
with col1:
    st.header("Inputs (Live Sensor Feed)")
    st.subheader(f"🌡️ Temperature: **{st.session_state.data['temp']} °C**")
    st.subheader(f"☀️ Light Level: **{st.session_state.data['light']}**")
    st.subheader(f"🏃 Motion: **{st.session_state.data['motion']}**")

    st.header("Voice Control (Simulated)")
    voice_command = st.text_input("Enter command (e.g., 'turn on lights' or 'set lights auto'):")
    
    # --- *** THIS IS THE NEW, FIXED VOICE LOGIC *** ---
    if st.button("Send Voice Command"):
        cmd = voice_command.lower()
        
        # --- Check for Kitchen ---
        if "kitchen" in cmd:
            if "on" in cmd: st.session_state.data["kitchen_state"] = "ON"
            elif "off" in cmd: st.session_state.data["kitchen_state"] = "OFF"
        
        # --- Check for Entertainment ---
        if "entertainment" in cmd:
            if "on" in cmd: st.session_state.data["entertainment_state"] = "ON"
            elif "off" in cmd: st.session_state.data["entertainment_state"] = "OFF"
        
        # --- Check for Lighting ---
        if "light" in cmd or "lighting" in cmd:
            if "auto" in cmd:
                st.session_state.data["light_mode"] = "AUTO"
            elif "on" in cmd:
                st.session_state.data["light_mode"] = "VOICE"
                st.session_state.data["light_voice_command"] = "ON"
            elif "off" in cmd:
                st.session_state.data["light_mode"] = "VOICE"
                st.session_state.data["light_voice_command"] = "OFF"

        # --- Check for HVAC ---
        if "hvac" in cmd or "air" in cmd or "cooling" in cmd:
            if "auto" in cmd:
                st.session_state.data["hvac_mode"] = "AUTO"
            elif "on" in cmd:
                st.session_state.data["hvac_mode"] = "VOICE"
                st.session_state.data["hvac_voice_command"] = "ON"
            elif "off" in cmd:
                st.session_state.data["hvac_mode"] = "VOICE"
                st.session_state.data["hvac_voice_command"] = "OFF"

# --- COLUMN 2: Outputs (ML-Driven Decisions) ---
with col2:
    st.header("Outputs (Appliance Control)")
    
    # --- Prepare data for ML model ---
    try:
        temp = float(st.session_state.data['temp'])
        light = int(st.session_state.data['light'])
        motion_str = st.session_state.data['motion']
        motion_encoded = motion_encoder.transform([motion_str])[0]
        current_features = np.array([[temp, light, motion_encoded, current_hour]])
        
        hvac_pred = hvac_model.predict(current_features)[0]
        light_pred = light_model.predict(current_features)[0]

    except Exception:
        hvac_pred = "OFF"
        light_pred = "OFF"
    
    # --- *** THIS IS THE FIXED DISPLAY LOGIC *** ---
    
    # --- Display: HVAC System ---
    st.subheader("❄️ HVAC System")
    if st.session_state.data["hvac_mode"] == "VOICE":
        # Voice command has priority
        state = st.session_state.data["hvac_voice_command"]
        if state == "ON":
            st.error(f"Status: **ON** (Reason: **Voice Command**)")
            st.session_state.client.publish("myhome/control/hvac", "ON")
        else:
            st.success(f"Status: **OFF** (Reason: **Voice Command**)")
            st.session_state.client.publish("myhome/control/hvac", "OFF")
    else:
        # ML model is in control
        if hvac_pred == "ON":
            st.error(f"Status: **ON** (Reason: **ML Prediction**)")
            st.session_state.client.publish("myhome/control/hvac", "ON")
        else:
            st.success(f"Status: **OFF** (Reason: **ML Prediction**)")
            st.session_state.client.publish("myhome/control/hvac", "OFF")

    # --- Display: Lighting System ---
    st.subheader("💡 Lighting System")
    if st.session_state.data["light_mode"] == "VOICE":
        # Voice command has priority
        state = st.session_state.data["light_voice_command"]
        if state == "ON":
            st.error(f"Status: **ON** (Reason: **Voice Command**)")
            st.session_state.client.publish("myhome/control/light", "ON")
        else:
            st.success(f"Status: **OFF** (Reason: **Voice Command**)")
            st.session_state.client.publish("myhome/control/light", "OFF")
    else:
        # ML model is in control
        if light_pred == "ON":
            st.error(f"Status: **ON** (Reason: **ML Prediction**)")
            st.session_state.client.publish("myhome/control/light", "ON")
        else:
            st.success(f"Status: **OFF** (Reason: **ML Prediction**)")
            st.session_state.client.publish("myhome/control/light", "OFF")

    # --- Voice-Controlled sections ---
    st.subheader("🍳 Kitchen Appliances")
    if st.session_state.data["kitchen_state"] == "ON":
        st.error("Status: **ON** (Reason: Voice Command)")
        st.session_state.client.publish("myhome/control/kitchen", "ON")
    else:
        st.success("Status: **OFF**")
        st.session_state.client.publish("myhome/control/kitchen", "OFF")
        
    st.subheader("📺 Entertainment Devices")
    if st.session_state.data["entertainment_state"] == "ON":
        st.error("Status: **ON** (Reason: Voice Command)")
        st.session_state.client.publish("myhome/control/entertainment", "ON")
    else:
        st.success("Status: **OFF**")
        st.session_state.client.publish("myhome/control/entertainment", "OFF")

# --- 9. Auto-Refresh Loop ---
time.sleep(1)
st.rerun()