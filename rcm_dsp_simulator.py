# # rcm_dsp_simulator.py
# import time
# import json
# import random
# import numpy as np
# import paho.mqtt.client as mqtt

# MQTT_BROKER = "localhost"
# MQTT_PORT = 1883
# MQTT_TOPIC = "sensor/frequency"

# client = mqtt.Client()
# client.connect(MQTT_BROKER, MQTT_PORT, 60)

# def simulate_rcm_signal():
#     # Simulate leakage current: normal <0.5, threat >0.5
#     leakage_current = random.uniform(0.0, 1.0)
#     return leakage_current

# def dsp_convert_to_frequency(leakage_current):
#     # Simulate DSP: convert to "frequency domain features"
#     # For simplicity, take FFT of random waveform scaled by leakage
#     time_signal = np.sin(np.linspace(0, 2*np.pi, 8)) * leakage_current
#     freq_features = np.abs(np.fft.fft(time_signal))[:4]  # keep 4 features
#     return freq_features.tolist()

# while True:
#     leakage = simulate_rcm_signal()
#     freq_data = dsp_convert_to_frequency(leakage)
#     payload = {"leakage_current": leakage, "freq_features": freq_data}
    
#     client.publish(MQTT_TOPIC, json.dumps(payload))
#     print(f"Published: {payload}")
#     time.sleep(1)
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

# Fence operating frequency in Hz (example)
FENCE_FREQ = 50

def simulate_rcm_signal():
    # Leakage current with random threat intensities
    leakage_current = random.uniform(0.0, 1.0)
    return leakage_current

def dsp_convert_to_frequency(leakage_current, threat=False):
    # Time signal parameters
    sample_rate = 256  # samples per second
    length = 64       # number of samples (longer for better resolution)
    t = np.linspace(0, length / sample_rate, length, endpoint=False)
    
    # Base sine wave at fence frequency
    base_signal = np.sin(2 * np.pi * FENCE_FREQ * t)
    
    # Add harmonics and noise
    harmonics = 0.3 * np.sin(2 * np.pi * 2 * FENCE_FREQ * t) + 0.15 * np.sin(2 * np.pi * 3 * FENCE_FREQ * t)
    noise = 0.1 * np.random.normal(size=length)
    
    # Threat modulation: frequency shift or amplitude increase
    if threat:
        mod_freq = FENCE_FREQ * random.uniform(0.8, 1.2)  # frequency deviation +/-20%
        mod_signal = 1.5 * np.sin(2 * np.pi * mod_freq * t)
        time_signal = leakage_current * (mod_signal + harmonics + noise)
    else:
        time_signal = leakage_current * (base_signal + harmonics + noise)
    
    freq_features = np.abs(np.fft.fft(time_signal))[:8]  # take 8 frequency bins for richer features
    return freq_features.tolist()

def simulate_tdr_fault():
    # Simulate TDR fault distance in meters (0 to 1000)
    # 0 means no fault detected
    if random.random() < 0.3:  # 30% chance of fault
        return round(random.uniform(1, 1000), 2)
    return 0

def simulate_lat_lon_in_kerala():
    lat = random.uniform(8.0, 12.0)
    lon = random.uniform(74.0, 77.0)
    return lat, lon

while True:
    leakage = simulate_rcm_signal()
    threat_flag = leakage > 0.5  # simple threat threshold
    
    freq_data = dsp_convert_to_frequency(leakage, threat=threat_flag)
    tdr_distance = simulate_tdr_fault()
    lat, lon = simulate_lat_lon_in_kerala()
    
    payload = {
        "leakage_current": leakage,
        "freq_features": freq_data,
        "tdr_distance": tdr_distance,
        "latitude": lat,
        "longitude": lon
    }
    
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print(f"Published: {payload}")
    time.sleep(1)
