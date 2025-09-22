import spacy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model 'en_core_web_sm' loaded successfully.")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found.")
    logger.error("Please run: python -m spacy download en_core_web_sm")
    nlp = None 

def analyze_message(message):
    # Figure out what the user wants based on their message
    if nlp is None:
         logger.warning("spaCy model not loaded. Skipping NLU analysis.")
         return {"intent": "general", "entities": []}  # Just return general intent if NLU isn't working

    doc = nlp(message)

    entities = [(ent.label_, ent.text) for ent in doc.ents]
    logger.debug(f"Entities found: {entities}")

    lower_message = message.lower()
    intent = "general" # Default intent
    
    # Enhanced intent detection
    if any(word in lower_message for word in ["weather", "temperature", "forecast"]):
        intent = "get_weather"
    elif any(word in lower_message for word in ["joke", "funny", "laugh"]):
        intent = "tell_joke"
    elif any(word in lower_message for word in ["time", "hour", "clock"]):
        intent = "get_time"

    logger.debug(f"Detected intent: {intent}")
    return {"intent": intent, "entities": entities}

def fetch_weather(entities):
    # Replace with real weather API logic
    location = "your location" # Default location
    if entities:
         gpe_entities = [entity[1] for entity in entities if entity[0] == "GPE"]
         if gpe_entities:
              location = gpe_entities[0] # Take the first one found
         else:
              loc_entities = [entity[1] for entity in entities if entity[0] == "LOC"]
              if loc_entities:
                   location = loc_entities[0]

    return f"I don't have real-time weather data, but let's pretend the weather in {location} is pleasant."
