import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

print("Starting model training (new, error-free method)...")

# --- 1. THE DATA (Embedded as a Python List) ---
# This method avoids all CSV-related errors.
data_list = [
    [22.1, 130, 'NONE', 0, 'OFF', 'OFF'],
    [33.5, 12, 'DETECTED', 1, 'ON', 'ON'],
    [25.3, 16, 'DETECTED', 2, 'OFF', 'ON'],
    [28.3, 161, 'NONE', 3, 'ON', 'OFF'],
    [31.8, 110, 'DETECTED', 4, 'ON', 'ON'],
    [19.0, 72, 'NONE', 5, 'OFF', 'OFF'],
    [27.0, 83, 'DETECTED', 6, 'OFF', 'ON'],
    [34.0, 430, 'NONE', 7, 'ON', 'OFF'],
    [23.0, 681, 'DETECTED', 8, 'OFF', 'OFF'],
    [26.9, 800, 'NONE', 9, 'OFF', 'OFF'],
    [21.8, 750, 'DETECTED', 10, 'OFF', 'OFF'],
    [29.2, 250, 'DETECTED', 11, 'ON', 'ON'],
    [30.5, 900, 'NONE', 12, 'ON', 'OFF'],
    [33.1, 850, 'DETECTED', 13, 'ON', 'OFF'],
    [24.5, 210, 'DETECTED', 14, 'OFF', 'ON'],
    [20.7, 500, 'NONE', 15, 'OFF', 'OFF'],
    [28.1, 600, 'DETECTED', 16, 'ON', 'OFF'],
    [27.5, 700, 'NONE', 17, 'OFF', 'OFF'],
    [31.0, 280, 'DETECTED', 18, 'ON', 'ON'],
    [23.2, 450, 'NONE', 19, 'OFF', 'OFF'],
    [26.2, 150, 'DETECTED', 20, 'OFF', 'ON'],
    [29.5, 80, 'NONE', 21, 'ON', 'OFF'],
    [33.8, 40, 'DETECTED', 22, 'ON', 'ON'],
    [21.1, 10, 'NONE', 23, 'OFF', 'OFF'],
    [23.5, 145, 'NONE', 0, 'OFF', 'OFF'],
    [31.2, 18, 'DETECTED', 1, 'ON', 'ON'],
    [26.7, 25, 'DETECTED', 2, 'OFF', 'ON'],
    [27.9, 180, 'NONE', 3, 'OFF', 'OFF'],
    [30.3, 120, 'DETECTED', 4, 'ON', 'ON'],
    [20.2, 80, 'NONE', 5, 'OFF', 'OFF'],
    [25.8, 90, 'DETECTED', 6, 'OFF', 'ON'],
    [32.7, 400, 'NONE', 7, 'ON', 'OFF'],
    [24.1, 700, 'DETECTED', 8, 'OFF', 'OFF'],
    [28.0, 820, 'NONE', 9, 'OFF', 'OFF'],
    [20.9, 780, 'DETECTED', 10, 'OFF', 'OFF'],
    [30.1, 280, 'DETECTED', 11, 'ON', 'ON'],
    [29.7, 920, 'NONE', 12, 'ON', 'OFF'],
    [31.6, 880, 'DETECTED', 13, 'ON', 'OFF'],
    [25.9, 230, 'DETECTED', 14, 'OFF', 'ON'],
    [22.3, 530, 'NONE', 15, 'OFF', 'OFF'],
    [27.6, 620, 'DETECTED', 16, 'OFF', 'OFF'],
    [26.8, 710, 'NONE', 17, 'OFF', 'OFF'],
    [31.5, 290, 'DETECTED', 18, 'ON', 'ON'],
    [24.3, 470, 'NONE', 19, 'OFF', 'OFF'],
    [25.1, 160, 'DETECTED', 20, 'OFF', 'ON'],
    [30.6, 90, 'NONE', 21, 'ON', 'OFF'],
    [32.4, 50, 'DETECTED', 22, 'ON', 'ON'],
    [22.6, 20, 'NONE', 23, 'OFF', 'OFF'],
    [24.8, 135, 'NONE', 0, 'OFF', 'OFF'],
    [30.8, 14, 'DETECTED', 1, 'ON', 'ON'],
    [25.0, 21, 'DETECTED', 2, 'OFF', 'ON'],
    [28.8, 140, 'NONE', 3, 'ON', 'OFF'],
    [31.1, 130, 'DETECTED', 4, 'ON', 'ON'],
    [19.5, 60, 'NONE', 5, 'OFF', 'OFF'],
    [26.3, 70, 'DETECTED', 6, 'OFF', 'ON'],
    [33.3, 410, 'NONE', 7, 'ON', 'OFF'],
    [23.7, 690, 'DETECTED', 8, 'OFF', 'OFF'],
    [27.2, 810, 'NONE', 9, 'OFF', 'OFF'],
    [21.4, 760, 'DETECTED', 10, 'OFF', 'OFF'],
    [29.8, 260, 'DETECTED', 11, 'ON', 'ON'],
    [30.0, 910, 'NONE', 12, 'ON', 'OFF'],
    [33.6, 860, 'DETECTED', 13, 'ON', 'OFF'],
    [24.9, 220, 'DETECTED', 14, 'OFF', 'ON'],
    [21.0, 510, 'NONE', 15, 'OFF', 'OFF'],
    [28.5, 610, 'DETECTED', 16, 'ON', 'OFF'],
    [27.1, 720, 'NONE', 17, 'OFF', 'OFF'],
    [30.7, 270, 'DETECTED', 18, 'ON', 'ON'],
    [23.9, 460, 'NONE', 19, 'OFF', 'OFF'],
    [26.6, 170, 'DETECTED', 20, 'OFF', 'ON'],
    [29.0, 100, 'NONE', 21, 'ON', 'OFF'],
    [33.0, 60, 'DETECTED', 22, 'ON', 'ON'],
    [21.5, 30, 'NONE', 23, 'OFF', 'OFF'],
    [22.9, 150, 'NONE', 0, 'OFF', 'OFF'],
    [32.1, 11, 'DETECTED', 1, 'ON', 'ON'],
    [26.1, 19, 'DETECTED', 2, 'OFF', 'ON'],
    [28.2, 170, 'NONE', 3, 'ON', 'OFF'],
    [31.4, 115, 'DETECTED', 4, 'ON', 'ON'],
    [19.8, 68, 'NONE', 5, 'OFF', 'OFF'],
    [27.3, 88, 'DETECTED', 6, 'OFF', 'ON'],
    [34.2, 420, 'NONE', 7, 'ON', 'OFF'],
    [23.3, 670, 'DETECTED', 8, 'OFF', 'OFF'],
    [26.5, 790, 'NONE', 9, 'OFF', 'OFF'],
    [22.0, 740, 'DETECTED', 10, 'OFF', 'OFF'],
    [29.4, 240, 'DETECTED', 11, 'ON', 'ON'],
    [30.9, 890, 'NONE', 12, 'ON', 'OFF'],
    [32.9, 840, 'DETECTED', 13, 'ON', 'OFF'],
    [25.4, 200, 'DETECTED', 14, 'OFF', 'ON'],
    [20.5, 520, 'NONE', 15, 'OFF', 'OFF'],
    [28.9, 630, 'DETECTED', 16, 'ON', 'OFF'],
    [27.8, 730, 'NONE', 17, 'OFF', 'OFF'],
    [31.3, 260, 'DETECTED', 18, 'ON', 'ON'],
    [24.6, 480, 'NONE', 19, 'OFF', 'OFF'],
    [25.5, 180, 'DETECTED', 20, 'OFF', 'ON'],
    [29.3, 110, 'NONE', 21, 'ON', 'OFF'],
    [32.0, 70, 'DETECTED', 22, 'ON', 'ON'],
    [21.9, 40, 'NONE', 23, 'OFF', 'OFF']
]

# 2. Load Data into a DataFrame
column_names = ['temp', 'light', 'motion', 'hour_of_day', 'hvac_action', 'light_action']
data = pd.DataFrame(data_list, columns=column_names)

# 3. Preprocess Data
le_motion = LabelEncoder()
data['motion_encoded'] = le_motion.fit_transform(data['motion'])

features = ['temp', 'light', 'motion_encoded', 'hour_of_day']
y_hvac = data['hvac_action']
y_light = data['light_action']
X = data[features] # X now contains only numeric data

# 4. Train HVAC Model
print("Training HVAC model...")
hvac_model = DecisionTreeClassifier(random_state=42)
hvac_model.fit(X, y_hvac)
joblib.dump(hvac_model, 'hvac_model.joblib')

# 5. Train Light Model
print("Training Light model...")
light_model = DecisionTreeClassifier(random_state=42)
light_model.fit(X, y_light)
joblib.dump(light_model, 'light_model.joblib')

# 6. Save the encoder
joblib.dump(le_motion, 'motion_encoder.joblib')

print("---")
print("Training complete. Models saved:")
print(" - hvac_model.joblib")
print(" - light_model.joblib")
print(" - motion_encoder.joblib")