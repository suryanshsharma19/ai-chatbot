import requests
from datetime import datetime

def handle_intent(intent, entities):
    if intent == "get_weather":
        return fetch_weather(entities)
    elif intent == "tell_joke":
        return fetch_joke()
    elif intent == "get_time":
        return get_current_time()
    return None

def fetch_weather(entities):
    # Replace with real weather API logic
    location = next((entity[1] for entity in entities if entity[0] == "GPE"), "your location")
    return f"The weather in {location} is sunny and 25°C."

def fetch_joke():
    # Example joke API
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        joke = response.json()
        return f"{joke['setup']} - {joke['punchline']}"
    return "Sorry, I couldn't fetch a joke right now."

def get_current_time():
    return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
