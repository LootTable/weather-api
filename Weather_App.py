from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Weather API is running"}

@app.get("/weather/{city}")
def get_weather(city: str):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(geo_url)
    geo_data = geo_response.json()

    if not geo_data.get("results"):
        return {"error": f"City '{city}' not found"}

    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]
    city_name = geo_data["results"][0]["name"]
    country = geo_data["results"][0]["country"]

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    current = weather_data["current_weather"]
    temp_f = round((current["temperature"] * 9/5) + 32)
    wind_mph = round(current["windspeed"] * 0.621371)

    return {
        "city": city_name,
        "country": country,
        "temperature_f": temp_f,
        "wind_speed_mph": wind_mph,
        "weather_code": current["weathercode"]
    }

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Weather Dashboard</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      min-height: 100vh;
      background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
      display: flex; align-items: center; justify-content: center;
      color: white;
    }
    .card {
      background: rgba(255,255,255,0.08);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 24px;
      padding: 2.5rem;
      width: 380px;
      text-align: center;
    }
    h1 { font-size: 22px; font-weight: 500; opacity: 0.7; margin-bottom: 1.5rem; letter-spacing: 2px; text-transform: uppercase; }
    .search { display: flex; gap: 8px; margin-bottom: 2rem; }
    input {
      flex: 1; padding: 12px 16px; border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.2);
      background: rgba(255,255,255,0.1); color: white;
      font-size: 15px; outline: none;
    }
    input::placeholder { color: rgba(255,255,255,0.4); }
    input:focus { border-color: rgba(255,255,255,0.5); }
    button {
      padding: 12px 20px; border-radius: 12px; border: none;
      background: rgba(255,255,255,0.2); color: white;
      font-size: 15px; cursor: pointer; transition: all 0.2s;
    }
    button:hover { background: rgba(255,255,255,0.3); }
    .weather-icon { font-size: 80px; margin: 1rem 0; line-height: 1; }
    .temp { font-size: 72px; font-weight: 300; margin: 0.5rem 0; }
    .temp sup { font-size: 28px; vertical-align: super; }
    .city-name { font-size: 24px; font-weight: 500; margin-bottom: 4px; }
    .country { font-size: 14px; opacity: 0.6; margin-bottom: 1.5rem; }
    .stats {
      display: grid; grid-template-columns: 1fr 1fr;
      gap: 12px; margin-top: 1.5rem;
    }
    .stat {
      background: rgba(255,255,255,0.07);
      border-radius: 14px; padding: 1rem;
    }
    .stat-label { font-size: 11px; opacity: 0.5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
    .stat-value { font-size: 20px; font-weight: 500; }
    .error { color: #ff6b6b; font-size: 14px; margin-top: 1rem; }
    .hidden { display: none; }
    .loading { opacity: 0.5; font-size: 14px; margin-top: 1rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Weather</h1>
    <div class="search">
      <input type="text" id="city-input" placeholder="Enter a city..." />
      <button onclick="fetchWeather()">Go</button>
    </div>
    <div class="loading hidden" id="loading">Fetching weather...</div>
    <div id="result" class="hidden">
      <div class="weather-icon" id="icon">🌤</div>
      <div class="temp"><span id="temp">--</span><sup>°F</sup></div>
      <div class="city-name" id="city">--</div>
      <div class="country" id="country">--</div>
      <div class="stats">
        <div class="stat">
          <div class="stat-label">Wind</div>
          <div class="stat-value"><span id="wind">--</span> mph</div>
        </div>
        <div class="stat">
          <div class="stat-label">Condition</div>
          <div class="stat-value" id="condition">--</div>
        </div>
      </div>
    </div>
    <div class="error hidden" id="error"></div>
  </div>

  <script>
    function getIcon(code) {
      if (code === 0) return "☀️";
      if (code <= 2) return "🌤️";
      if (code === 3) return "☁️";
      if (code <= 48) return "🌫️";
      if (code <= 57) return "🌦️";
      if (code <= 67) return "🌧️";
      if (code <= 77) return "🌨️";
      if (code <= 82) return "🌦️";
      if (code <= 99) return "⛈️";
      return "🌡️";
    }

    function getCondition(code) {
      if (code === 0) return "Clear";
      if (code <= 2) return "Mostly Clear";
      if (code === 3) return "Overcast";
      if (code <= 48) return "Foggy";
      if (code <= 57) return "Drizzle";
      if (code <= 67) return "Rainy";
      if (code <= 77) return "Snowy";
      if (code <= 82) return "Showers";
      if (code <= 99) return "Thunderstorm";
      return "Unknown";
    }

    document.getElementById('city-input').addEventListener('keydown', e => {
      if (e.key === 'Enter') fetchWeather();
    });

    async function fetchWeather() {
      const city = document.getElementById('city-input').value.trim();
      if (!city) return;

      const errorEl = document.getElementById('error');
      const resultEl = document.getElementById('result');
      const loadingEl = document.getElementById('loading');

      errorEl.classList.add('hidden');
      resultEl.classList.add('hidden');
      loadingEl.classList.remove('hidden');

      try {
        const res = await fetch('/weather/' + encodeURIComponent(city));
        const data = await res.json();
        loadingEl.classList.add('hidden');

        if (data.error) {
          errorEl.textContent = data.error;
          errorEl.classList.remove('hidden');
          return;
        }

        const code = data.weather_code;
        document.getElementById('icon').textContent = getIcon(code);
        document.getElementById('temp').textContent = data.temperature_f;
        document.getElementById('city').textContent = data.city;
        document.getElementById('country').textContent = data.country;
        document.getElementById('wind').textContent = data.wind_speed_mph;
        document.getElementById('condition').textContent = getCondition(code);
        resultEl.classList.remove('hidden');

      } catch(e) {
        loadingEl.classList.add('hidden');
        errorEl.textContent = "Something went wrong. Is the server running?";
        errorEl.classList.remove('hidden');
      }
    }
  </script>
</body>
</html>
"""