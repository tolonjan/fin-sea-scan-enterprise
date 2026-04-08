from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import random

app = FastAPI()

# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINTRAFFIC_URL = "https://meri.digitraffic.fi/api/ais/v1/locations"

# -------------------------
# PORT DATA
# -------------------------
PORTS = [
    {"name": "Helsinki", "lat": 60.17, "lon": 24.94},
    {"name": "Stockholm", "lat": 59.33, "lon": 18.06},
    {"name": "Tallinn", "lat": 59.44, "lon": 24.75},
    {"name": "Turku", "lat": 60.45, "lon": 22.27},
]

def closest_port(lat, lon):
    best = None
    best_dist = 999999

    for port in PORTS:
        d = math.hypot(lat - port["lat"], lon - port["lon"])
        if d < best_dist:
            best = port
            best_dist = d

    return best

# -------------------------
# HEALTH CHECK
# -------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# -------------------------
# SHIPS (SAFE VERSION)
# -------------------------
@app.get("/ships")
def get_ships():
    try:
        res = requests.get(FINTRAFFIC_URL, timeout=10)
        data = res.json()
    except Exception as e:
        return {"error": "Fintraffic fetch failed", "details": str(e)}

    ships = []

    for ship in data.get("features", []):

        try:
            geometry = ship.get("geometry")
            props = ship.get("properties")

            if not geometry or not props:
                continue

            coords = geometry.get("coordinates")
            if not coords or len(coords) < 2:
                continue

            lon, lat = coords[0], coords[1]

            mmsi = props.get("mmsi")
            if not mmsi:
                continue

            speed = props.get("sog") or 0
            cog = props.get("cog")
            heading = props.get("trueHeading")

            port = closest_port(lat, lon)

            # ETA calculation (safe)
            distance = abs(lat - port["lat"]) + abs(lon - port["lon"])
            eta = distance / (speed / 10 + 0.1)

            ships.append({
                "mmsi": mmsi,
                "lat": lat,
                "lon": lon,
                "speed": round(speed, 1),
                "cog": cog,
                "heading": heading,
                "destination": port["name"],
                "eta": round(eta, 1)
            })

        except Exception:
            # skip broken ship
            continue

    return ships[:300]

# -------------------------
# HISTORY (SIMULATED TRACK)
# -------------------------
@app.get("/history/{mmsi}")
def get_history(mmsi: int):

    lat = 60 + random.random()
    lon = 24 + random.random()

    points = []

    for i in range(20):
        lat += random.uniform(-0.05, 0.05)
        lon += random.uniform(-0.05, 0.05)

        points.append({
            "lat": lat,
            "lon": lon
        })

    return points

# -------------------------
# SIMPLE ANALYTICS
# -------------------------
@app.get("/stats")
def stats():

    ships = get_ships()

    if isinstance(ships, dict):
        return ships

    total = len(ships)
    avg_speed = sum(s["speed"] for s in ships) / total if total else 0

    return {
        "total_vessels": total,
        "avg_speed": round(avg_speed, 1),
        "estimated_24h": total * 24
    }
