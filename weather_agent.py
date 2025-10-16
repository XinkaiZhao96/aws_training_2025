import os
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands_tools import http_request

# Create BedrockAgentCoreApp instance
app = BedrockAgentCoreApp()

# API configurations
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "38a9c7392c1c9a1caf60671941d3d98b")
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY", "nwttAG9nkHpsdXASbnXscNskfZixQydV")
TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
SUNRISE_SUNSET_BASE_URL = "https://api.sunrise-sunset.org/json"

# Set up Agent with http_request tool and comprehensive prompt
agent = Agent(
    tools=[http_request],
    system_prompt=f"""You are a comprehensive city information assistant that can provide weather, events, and sunrise/sunset information. 

CAPABILITIES:
1. Weather Information
2. Event Search (via Ticketmaster)
3. Sunrise/Sunset Times

WEATHER QUERIES:
When users ask about weather in a city:
1. Use http_request to call: {OPENWEATHER_BASE_URL}?q={{city}}&appid={OPENWEATHER_API_KEY}&units=metric
2. Parse and format: temperature, conditions, humidity, city/country info

EVENT QUERIES:
When users ask about events in a city:
1. Use http_request to call: {TICKETMASTER_BASE_URL}?city={{city}}&apikey={TICKETMASTER_API_KEY}
2. Parse and format: event names, dates, venues, descriptions from the Ticketmaster API response
3. Handle the JSON response structure with _embedded.events array containing event details
4. If no Ticketmaster API key is available, inform the user that event search requires API key configuration

SUNRISE/SUNSET QUERIES:
When users ask about sunrise/sunset times:
1. First get coordinates using weather API: {OPENWEATHER_BASE_URL}?q={{city}}&appid={OPENWEATHER_API_KEY}
2. Extract lat/lon from the response
3. Use http_request to call: {SUNRISE_SUNSET_BASE_URL}?lat={{lat}}&lng={{lon}}&formatted=0
4. Parse and format: sunrise/sunset times in local timezone

MULTI-FEATURE QUERIES:
Handle requests that combine multiple features (e.g., "Tell me about weather and events in London")

Always provide helpful, conversational responses. If an API is unavailable or returns errors, provide clear explanations."""
)

@app.entrypoint
def invoke(payload):
    """Handle user requests for weather information"""
    user_message = payload.get("prompt", "Hello! How can I help you with weather information today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    # For local testing
    app.run()