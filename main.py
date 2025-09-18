from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt
import json
from ai_model import predict_threat
from collections import deque
import asyncio

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store alerts in memory
alerts = deque(maxlen=50)
websockets = []

# ✅ Global loop variable
event_loop = None


@app.on_event("startup")
async def startup_event():
    """Capture FastAPI's event loop on startup"""
    global event_loop
    event_loop = asyncio.get_event_loop()


# WebSocket endpoint for frontend
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     websockets.append(websocket)
#     try:
#         while True:
#             await websocket.receive_text()
#     except:
#         websockets.remove(websocket)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keeps connection alive
    except:
        websockets.remove(websocket)


# MQTT setup
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/frequency"


# def on_message(client, userdata, msg):
#     global event_loop
#     data = json.loads(msg.payload)
#     freq_features = data["freq_features"]
#     leakage = data["leakage_current"]

#     if predict_threat(freq_features):
#         alert = {
#             "threat": True,
#             "leakage_current": leakage,
#             "x": round(10 * leakage, 2),
#             "y": round(5 * leakage, 2),
#         }
#         alerts.append(alert)

#         # ✅ Schedule WebSocket send on FastAPI’s loop
#         if event_loop:
#             for ws in websockets:
#                 asyncio.run_coroutine_threadsafe(ws.send_json(alert), event_loop)

#         print(f"🔥 RELAY TRIGGERED: {alert}")
#     else:
#         print(f"Normal: {data}")
def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    
    freq_features = data.get("freq_features")
    leakage = data.get("leakage_current")
    tdr_distance = data.get("tdr_distance", 0)  # default 0 if missing
    latitude = data.get("latitude", None)
    longitude = data.get("longitude", None)
    
    # Predict threat based on freq_features
    if freq_features and predict_threat(freq_features):
        alert = {
            "threat": True,
            "leakage_current": leakage,
            "tdr_distance": tdr_distance,
            "latitude": latitude,
            "longitude": longitude,
            "x": round(10 * leakage, 2),
            "y": round(5 * leakage, 2)
        }
        alerts.append(alert)
        for ws in websockets:
            asyncio.run_coroutine_threadsafe(ws.send_json(alert), main_loop)
        print(f"🔥 RELAY TRIGGERED: {alert}")
    else:
        print(f"Normal: {data}")


client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.on_message = on_message
client.loop_start()


@app.get("/alerts")
def get_alerts():
    return list(alerts)
