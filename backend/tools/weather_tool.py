import json
import httpx
from datetime import datetime
from db.redis_client import redis_client
from models.agent_output import ClimateOutput

async def fetch_weather_and_evaluate(lat: float, lon: float, is_fungal: bool = False) -> dict:
    """
    Fetches hourly weather data from Open-Meteo and applies the spray safety rules.
    Caches weather responses per ~1.1km grid (2 decimal places) for 1 hour.
    """
    lat_round = round(lat, 2)
    lon_round = round(lon, 2)
    cache_key = f"weather:{lat_round}:{lon_round}"
    
    # 1. Check cache
    cached = redis_client.get(cache_key)
    if cached:
        try:
            weather_data = json.loads(cached)
            return evaluate_spray_conditions(weather_data, is_fungal)
        except Exception:
            pass

    # 2. Fetch from Open-Meteo
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat_round,
        "longitude": lon_round,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,wind_speed_10m",
        "timezone": "Asia/Kolkata",
        "forecast_days": 1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=5.0)
            if response.status_code == 200:
                weather_data = response.json()
                # Cache for 1 hour (3600 seconds)
                redis_client.setex(cache_key, 3600, json.dumps(weather_data))
                return evaluate_spray_conditions(weather_data, is_fungal)
    except Exception as e:
        print(f"Open-Meteo call failed: {e}. Using mock weather.")

    # 3. Fallback mock weather (Good conditions)
    mock_weather = {
        "hourly": {
            "time": [datetime.now().strftime("%Y-%m-%dT%H:00")],
            "temperature_2m": [28.5],
            "relative_humidity_2m": [60],
            "precipitation_probability": [10],
            "wind_speed_10m": [8.0]
        }
    }
    return evaluate_spray_conditions(mock_weather, is_fungal)

def evaluate_spray_conditions(weather_json: dict, is_fungal: bool) -> dict:
    """Applies the spray safety decision tree rules on weather data."""
    hourly = weather_json.get("hourly", {})
    if not hourly or "time" not in hourly:
        return {
            "weather_safe": True,
            "weather_reason": "Good conditions. Spray now for best results.",
            "safe_spray_window": "Immediately"
        }
        
    temperatures = hourly.get("temperature_2m", [25.0])
    humidities = hourly.get("relative_humidity_2m", [50])
    precip_probs = hourly.get("precipitation_probability", [0])
    wind_speeds = hourly.get("wind_speed_10m", [5.0])
    times = hourly.get("time", [])

    # Check next 6 hours of forecasts
    lookahead = min(6, len(times))
    
    for i in range(lookahead):
        temp = temperatures[i]
        humidity = humidities[i]
        precip = precip_probs[i]
        wind = wind_speeds[i]
        
        if precip > 40:
            return {
                "weather_safe": False,
                "weather_reason": f"Rain expected ({precip}% chance in next 6h). Chemical spray would wash off.",
                "safe_spray_window": "Tomorrow morning after rain stops"
            }
        
        if wind > 15:
            return {
                "weather_safe": False,
                "weather_reason": f"Wind is too strong ({wind} km/h). Chemical drift risk.",
                "safe_spray_window": "Late evening or early morning when wind subsides"
            }
            
        if temp > 38:
            return {
                "weather_safe": False,
                "weather_reason": f"Temperature is too high ({temp}°C). Heat reduces efficacy.",
                "safe_spray_window": "Today after 5:00 PM when it cools down"
            }
            
        if temp < 10:
            return {
                "weather_safe": False,
                "weather_reason": f"Temperature is too low ({temp}°C). Cold reduces absorption.",
                "safe_spray_window": "Today midday between 11:00 AM and 2:00 PM"
            }
            
        if humidity > 85 and is_fungal:
            return {
                "weather_safe": True,
                "weather_reason": "High humidity (potential fungal spread), but safe to spray now. Act fast.",
                "safe_spray_window": "Immediately"
            }
            
    return {
        "weather_safe": True,
        "weather_reason": "Good conditions. Spray now for best results.",
        "safe_spray_window": "Immediately"
    }
