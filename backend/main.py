from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FINTRAFFIC = "https://meri.digitraffic.fi/api/ais/v1/locations"
FMI = "https://opendata.fmi.fi/wfs"

API_KEYS = ["demo_key_123"]

# ---------------------------
# AUTH (simple paywall)
# ---------------------------
@app.middleware("http")
async def check_key(request: Request, call_next):
    if request.url.path.startswith("/public") or request.url.path.startswith("/weather"):
        return await call_next(request)

    key = request.headers.get("x-api-key")
    if key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return await call_next(request)

# ---------------------------
# SHIPS
# ---------------------------
@app.get("/public/ships")
def ships():
    return requests.get(FINTRAFFIC).json()

# ---------------------------
# ALERTS (simple logic)
# ---------------------------
@app.get("/enterprise/alerts")
def alerts():
    data = requests.get(FINTRAFFIC).json()
    result = []

    for ship in data.get("features", [])[:100]:
        speed = ship["properties"].get("sog", 0)

        risks = []
        if speed > 25:
            risks.append("High speed")

        if risks:
            result.append({
                "mmsi": ship["properties"]["mmsi"],
                "risks": risks
            })

    return result

# ---------------------------
# FMI WEATHER (REAL)
# ---------------------------
@app.get("/weather")
def weather():
    params = {
        "service": "WFS",
        "request": "getFeature",
        "storedquery_id": "fmi::observations::weather::simple",
        "parameters": "windspeedms"
    }

    res = requests.get(FMI, params=params)
    values = re.findall(r"<wml2:value>(.*?)</wml2:value>", res.text)

    result = []
    for v in values[:20]:
        try:
            result.append({"wind": float(v)})
        except:
            pass

    return result

# ---------------------------
# STRIPE PLACEHOLDER
# ---------------------------
@app.get("/create-checkout")
def create_checkout():
    return {
        "url": "https://buy.stripe.com/test_placeholder"
    }
