# AI-Powered Smart Home Simulation

This project simulates an AI-powered smart home as part of a CAO project.

It consists of two main components:
- `hardware_simulator.py`: A script that simulates IoT sensors (temp, light, motion) publishing data to an MQTT broker.
- `app.py`: A Streamlit web dashboard that acts as the "Edge AI" device. It subscribes to the sensor data, uses a machine learning model to make decisions, and provides a UI for voice control.
- `train_model.py`: A script to train the ML models from a CSV.

## How to Run
1. Install dependencies: `pip install streamlit paho-mqtt pandas scikit-learn joblib`
2. Run the hardware simulator: `python hardware_simulator.py`
3. In a separate terminal, run the app: `streamlit run app.py`