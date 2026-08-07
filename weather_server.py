import os
import requests
from mcp.server.fastmcp import FastMCP

OPENWEATHERMAP_API_KEY = "xxx"

#Initialize FastMCP server
mcp = FastMCP("WeatherAssistant")

@mcp.tool()
def get_weather(location: str) -> dict:
    """
    Fetches the current weather for a specified location using the OpenWeatherMap API.
    
    Args:
        location: The city name and optional country code (e.g London, UK).
        
    Returns:
        A dictionary containing weather information or an error message.
    """

    if not OPENWEATHERMAP_API_KEY:
        return {"error": "OpenWeatherMap API KEY is not configured on the server."}

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric" # Use "Imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        #Extracting relevant weather information
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return {
            "location": data["name"],
            "weather": weather_description,
            "temperature_celsius": f"{temperature}C",
            "feels_like_celcius": f"{feels_like}C",
            "humidity": f"{humidity}%",
            "wind_speed_mps": f"{wind_speed} m/s"
        }
