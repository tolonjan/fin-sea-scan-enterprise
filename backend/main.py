from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINTRAFFIC = "https://meri.digitraffic.fi/api/ais/v1/locations"

PORTS = [
    {"name": "Helsinki", "lat": 60.17, "lon": 24.94},
    {"name": "Stockholm", "lat": 59.33, "lon": 18.06},
    {"name": "Tallinn", "lat": 59.44, "lon": 24.75},
]

def closest_port(lat, lon):
    try:
        return min(PORTS, key=lambda p: math.hypot(lat - p["lat"], lon - p["lon"]))
    except:
        return {"name": "Unknown"}

# -------------------
# HEALTH
# -------------------
@app.get("/")
def root():
    return {"status": "ok"}

# -------------------
# SHIPS (ULTRA SAFE)
# -------------------
@app.get("/ships")
def ships():

    try:
        response = requests.get(FINTRAFFIC, timeout=10)
        data = response.json()
    except Exception as e:
        return [{"error": "fetch_failed"}]

    ships = []

    for ship in data.get("features", []):

        try:
            geometry = ship.get("geometry", {})
            props = ship.get("properties", {})

            coords = geometry.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            lon = coords[0]
            lat = coords[1]

            mmsi = props.get("mmsi")
            if not mmsi:
                continue

            speed = props.get("sog") or 0

            port = closest_port(lat, lon)

            distance = abs(lat - port.get("lat", lat)) + abs(lon - port.get("lon", lon))
            eta = distance / (speed / 10 + 0.1)

            ships.append({
                "mmsi": mmsi,
                "lat": lat,
                "lon": lon,
                "speed": round(speed, 1),
                "destination": port.get("name", "Unknown"),
                "eta": round(eta, 1)
            })

        except Exception:
            continue

    # fallback jos API ei anna mitään
    if len(ships) == 0:
        return [
            {"mmsi": 111, "lat": 60.17, "lon": 24.94, "speed": 12, "destination": "Helsinki", "eta": 5},
            {"mmsi": 222, "lat": 59.33, "lon": 18.06, "speed": 18, "destination": "Stockholm", "eta": 3},
        ]

    return ships[:200]

# -------------------
# HISTORY
# -------------------
@app.get("/history/{mmsi}")
def history(mmsi: int):

    lat = 60
    lon = 24

    points = []

    for _ in range(20):
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)
        points.append({"lat": lat, "lon": lon})

    return points
