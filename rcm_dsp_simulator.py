# rcm_dsp_simulator.py
import time
import json
import random
import numpy as np
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/frequency"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def simulate_rcm_signal():
    # Simulate leakage current: normal <0.5, threat >0.5
    leakage_current = random.uniform(0.0, 1.0)
    return leakage_current

def dsp_convert_to_frequency(leakage_current):
    # Simulate DSP: convert to "frequency domain features"
    # For simplicity, take FFT of random waveform scaled by leakage
    time_signal = np.sin(np.linspace(0, 2*np.pi, 8)) * leakage_current
    freq_features = np.abs(np.fft.fft(time_signal))[:4]  # keep 4 features
    return freq_features.tolist()

while True:
    leakage = simulate_rcm_signal()
    freq_data = dsp_convert_to_frequency(leakage)
    payload = {"leakage_current": leakage, "freq_features": freq_data}
    
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print(f"Published: {payload}")
    time.sleep(1)
