from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
import google.generativeai as genai
from memory import ConversationMemory
from intents import handle_intent
from nlu import analyze_message
import requests
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"

def init_gemini_client():
    # Set up the Google Gemini AI client for chat responses
    if not GOOGLE_API_KEY or GOOGLE_API_KEY in ["your_api_key_here", "test_disabled"]:
        logger.warning("Google API key not found or is placeholder. Please set GOOGLE_API_KEY in your .env file.")
        logger.info("Running in fallback mode without AI model.")
        return None
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info("Google Gemini client initialized successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to initialize Google Gemini client: {e}")
        logger.info("Running in fallback mode without AI model.")
        return None

def get_simple_response(message):
    # Provide basic responses when the AI model isn't available
    message_lower = message.lower()
    
    greetings = ["hello", "hi", "hey", "greetings"]
    if any(greeting in message_lower for greeting in greetings):
        return "Hello! How can I help you today?"
    
    questions = ["how are you", "how do you do"]
    if any(question in message_lower for question in questions):
        return "I'm doing well, thank you for asking! How can I assist you?"
    
    farewells = ["goodbye", "bye", "see you", "farewell"]
    if any(farewell in message_lower for farewell in farewells):
        return "Goodbye! Have a great day!"
    
    thanks = ["thank", "thanks"]
    if any(thank in message_lower for thank in thanks):
        return "You're welcome! Is there anything else I can help you with?"
    
    help_words = ["help", "assist", "support"]
    if any(help_word in message_lower for help_word in help_words):
        return "I'm here to help! You can ask me about the weather, jokes, time, or just have a conversation."
    
    # Default response
    return "I understand you're trying to communicate with me. While my advanced AI features aren't available right now, I can still help with basic questions about weather, jokes, and time!"

ai_client = init_gemini_client()

app = Flask(__name__)
memory = ConversationMemory(max_history=5)

@app.route('/')
def home():
    return "Chatbot API is running. Use the /chat endpoint.", 200

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"reply": "Error: Request must be JSON", "error": "Invalid content type"}), 400

    user_message = request.json.get("message", "")
    if not user_message.strip():
        logger.warning("Received empty message.")
        return jsonify({"reply": "Please provide a message."}), 400

    logger.info(f"Received message: {user_message}")

    # First try specific intents
    try:
        analysis = analyze_message(user_message)
        intent = analysis["intent"]
        entities = analysis["entities"]
        
        if intent != "general":
            try:
                custom_response = handle_intent(intent, entities)
                if custom_response:
                    logger.info(f"Handled intent '{intent}' with response: {custom_response}")
                    memory.add_message("user", user_message)
                    memory.add_message("assistant", custom_response)
                    return jsonify({"reply": custom_response})
            except Exception as e:
                logger.error(f"Intent handling failed: {e}")
    except Exception as e:
        logger.error(f"NLU analysis failed: {e}")

    # Fall back to the language model or simple responses
    if not ai_client:
        # Simple rule-based fallback responses
        memory.add_message("user", user_message)
        simple_response = get_simple_response(user_message)
        memory.add_message("assistant", simple_response)
        return jsonify({"reply": simple_response})

    try:
        # Add the user message to memory
        memory.add_message("user", user_message)
        
        # Get conversation history
        history = memory.get_formatted_history_string(include_system_prompt=True)
        
        # Set up retry mechanism
        max_retries = 3
        retry_delay = 2  # seconds
        last_error = None

        for attempt in range(max_retries):
            try:
                # Use thread-safe timeout with concurrent.futures
                import concurrent.futures
                
                def call_gemini_api():
                    # Generate response using Google Gemini
                    prompt = f"You are a helpful and friendly chatbot. Previous conversation:\n{history}\n\nRespond naturally and concisely to the user's message."
                    response_obj = ai_client.generate_content(prompt)
                    return response_obj.text
                
                try:
                    # Execute with timeout
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(call_gemini_api)
                        response = future.result(timeout=10)  # 10 second timeout
                except concurrent.futures.TimeoutError:
                    logger.warning(f"Gemini API timeout on attempt {attempt + 1}, falling back...")
                    raise requests.exceptions.Timeout("Gemini API timeout")

                # Clean up the response
                reply = response.strip()
                
                # Remove any model-generated prefixes
                if ":" in reply:
                    reply = reply.split(":", 1)[-1].strip()
                
                # Take only the first paragraph
                reply = reply.split('\n')[0].strip()
                
                # Fallback for empty or very short replies
                if not reply or len(reply) < 2:
                    reply = "I understand your message. Could you please provide more details?"
                
                # Add the response to memory and return
                memory.add_message("assistant", reply)
                return jsonify({"reply": reply})

            except (requests.exceptions.Timeout, TimeoutError):
                last_error = "Request timed out"
                logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out. Retrying...")
                if attempt == max_retries - 1:  # Last attempt
                    # Use fallback response immediately
                    fallback_response = get_simple_response(user_message)
                    memory.add_message("assistant", fallback_response)
                    return jsonify({"reply": fallback_response})
                time.sleep(retry_delay)
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error on attempt {attempt + 1}/{max_retries}: {e}")
                time.sleep(retry_delay)

        # If we get here, all retries failed
        logger.error(f"All retries failed. Last error: {last_error}")
        return jsonify({
            "reply": "I apologize, but I'm having trouble connecting to my language model. Please try again in a moment.",
            "error": last_error
        }), 500

    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        return jsonify({
            "reply": "I apologize, but I'm having trouble processing your message. Please try again.",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)