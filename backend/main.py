from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, math, random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINTRAFFIC = "https://meri.digitraffic.fi/api/ais/v1/locations"

# -------------------
# PORTS
# -------------------
PORTS = [
    {"name": "Helsinki", "lat": 60.17, "lon": 24.94},
    {"name": "Stockholm", "lat": 59.33, "lon": 18.06},
    {"name": "Tallinn", "lat": 59.44, "lon": 24.75},
]

def closest_port(lat, lon):
    best = None
    best_dist = 999

    for p in PORTS:
        d = math.hypot(lat - p["lat"], lon - p["lon"])
        if d < best_dist:
            best = p
            best_dist = d

    return best

# -------------------
# SHIPS (MAIN)
# -------------------
@app.get("/ships")
def ships():
    try:
        data = requests.get(FINTRAFFIC, timeout=10).json()
    except:
        return []

    result = []

    for ship in data.get("features", [])[:200]:
        lat = ship["geometry"]["coordinates"][1]
        lon = ship["geometry"]["coordinates"][0]

        speed = ship["properties"].get("sog", 0)
        mmsi = ship["properties"]["mmsi"]

        port = closest_port(lat, lon)

        distance = abs(lat - port["lat"]) + abs(lon - port["lon"])
        eta = distance / (speed / 10 + 0.1)

        result.append({
            "mmsi": mmsi,
            "lat": lat,
            "lon": lon,
            "speed": speed,
            "cog": ship["properties"].get("cog"),
            "heading": ship["properties"].get("trueHeading"),
            "destination": port["name"],
            "eta": round(eta, 1)
        })

    return result

# -------------------
# HISTORY
# -------------------
@app.get("/history/{mmsi}")
def history(mmsi: int):
    lat, lon = 60, 24
    points = []

    for i in range(15):
        lat += random.uniform(-0.1, 0.1)
        lon += random.uniform(-0.1, 0.1)
        points.append({"lat": lat, "lon": lon})

    return points

# -------------------
# HEALTH CHECK
# -------------------
@app.get("/")
def root():
    return {"status": "ok"}
