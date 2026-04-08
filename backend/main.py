from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINTRAFFIC = "https://meri.digitraffic.fi/api/ais/v1/locations"

API_KEYS = ["demo_key_123"]

@app.middleware("http")
async def check_key(request: Request, call_next):
    if request.url.path.startswith("/public"):
        return await call_next(request)

    key = request.headers.get("x-api-key")
    if key not in API_KEYS:
        raise HTTPException(status_code=401)

    return await call_next(request)

@app.get("/public/ships")
def ships():
    return requests.get(FINTRAFFIC).json()

@app.get("/enterprise/intelligence")
def intelligence():
    data = requests.get(FINTRAFFIC).json()
    result = []

    for ship in data.get("features", [])[:100]:
        result.append({
            "mmsi": ship["properties"]["mmsi"],
            "lat": ship["geometry"]["coordinates"][1],
            "lon": ship["geometry"]["coordinates"][0],
            "speed": ship["properties"].get("sog", 0)
        })

    return result
