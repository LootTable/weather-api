# Weather API

A REST API that returns real-time weather data for any city in the world.

Built with FastAPI and Python. Uses the Open-Meteo API — no API key required.

Features
- Search any city and get current temperature, wind speed, and conditions
- Includes a browser-based dashboard at `/dashboard`
- Returns temperature in °F and wind speed in mph

How to run it

Install dependencies:
```bash
pip3 install fastapi uvicorn requests
```

Start the server:
```bash
uvicorn Weather_App:app --reload
```

Open your browser and go to:
```
http://127.0.0.1:8000/dashboard
```

Endpoints

`GET /weather/{city}` — returns weather data as JSON

`GET /dashboard` — browser UI for searching cities

Tech used
- Python
- FastAPI
- Open-Meteo API
