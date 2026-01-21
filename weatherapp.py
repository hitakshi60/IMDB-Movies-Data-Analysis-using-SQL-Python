#Steps to run and test the Weather API:
#1.Create and activate virtual environment:python -m venv venv and activate using venv\Scripts\activate
#2.Install dependencies:pip install fastapi uvicorn requests
#3.Start the server using:python -m uvicorn weatherapp:app --reload
#4.Open another Command Prompt and run the curl commands.
#For JSON:curl -X POST "http://127.0.0.1:8000/getCurrentWeather" -H "Content-Type: application/json" -d "{\"city\":\"Bangalore\",\"output_format\":\"json\"}"
#For XML:curl -X POST "http://127.0.0.1:8000/getCurrentWeather" -H "Content-Type: application/json" -d "{\"city\":\"Bangalore\",\"output_format\":\"xml\"}"

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import xml.etree.ElementTree as ET

app = FastAPI(title="Weather API", version="1.0.0")


class WeatherRequest(BaseModel):
    city: str
    output_format: str


@app.get("/")
def servicecheck():
    return {
        "status": "running",
        "service": "Weather API"
    }


def fetch_weather(city: str) -> dict:
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    headers = {
        "X-RapidAPI-Key": "31371bc5c3msh34f399b07961d46p192883jsn2ba7562e3194",
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params={"q": city}, timeout=5)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Weather service unavailable")

    payload = response.json()

    if payload.get("error"):
        raise HTTPException(status_code=400, detail=payload["error"]["message"])

    location = payload["location"]
    current = payload["current"]

    return {
        "temperature": current["temp_c"],
        "latitude": location["lat"],
        "longitude": location["lon"],
        "city": f"{location['name']} {location['country']}"
    }


def serialize_xml(data: dict) -> str:
    root = ET.Element("root")
    ET.SubElement(root, "Temperature").text = str(data["temperature"])
    ET.SubElement(root, "City").text = data["city"]
    ET.SubElement(root, "Latitude").text = str(data["latitude"])
    ET.SubElement(root, "Longitude").text = str(data["longitude"])
    return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding="unicode")


@app.post("/getCurrentWeather")
def get_current_weather(request: WeatherRequest):
    format_type = request.output_format.strip().lower()

    if format_type not in {"json", "xml"}:
        raise HTTPException(status_code=400, detail="Unsupported response format")

    weather = fetch_weather(request.city.strip())

    if format_type == "json":
        return JSONResponse(content={
            "temperature": f"{weather['temperature']} C",
            "city": weather["city"],
            "latitude": weather["latitude"],
            "longitude": weather["longitude"]
        })

    return Response(
        content=serialize_xml(weather),
        media_type="application/xml"
    )
