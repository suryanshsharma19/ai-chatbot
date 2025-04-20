from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
from huggingface_hub import InferenceClient
from memory import ConversationMemory
from intents import handle_intent
from nlu import analyze_message
import requests
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Using a more conversational model
DEFAULT_MODEL_ID = "facebook/blenderbot-400M-distill"
HF_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID", DEFAULT_MODEL_ID)

def init_huggingface_client():
    """Initialize and test the Hugging Face client connection"""
    if not HF_API_TOKEN:
        logger.error("Hugging Face API token not found. Please set HUGGINGFACE_API_TOKEN in your .env file.")
        return None
    
    try:
        client = InferenceClient(
            token=HF_API_TOKEN,
            timeout=30  # Increase timeout to 30 seconds
        )
        
        # Test the connection with a simple query
        logger.info("Testing Hugging Face API connection...")
        test_response = client.text_generation(
            "Hello",
            model=HF_MODEL_ID,
            max_new_tokens=10,
            timeout=10
        )
        logger.info("Hugging Face API connection test successful")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Hugging Face client: {e}")
        return None

hf_client = init_huggingface_client()

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

    # Fall back to the language model
    if not hf_client:
        return jsonify({
            "reply": "I apologize, but my language model is currently unavailable. Please try again later.",
            "error": "Model not configured"
        }), 503

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
                # Generate response using the model with increased timeout
                response = hf_client.text_generation(
                    history,
                    model=HF_MODEL_ID,
                    max_new_tokens=150,
                    temperature=0.8,
                    top_p=0.95,
                    repetition_penalty=1.2,
                    do_sample=True,
                    stop_sequences=["\nUser:", "\nChatbot:", "<|endoftext|>"],
                    timeout=30  # 30 second timeout
                )

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

            except requests.exceptions.Timeout:
                last_error = "Request timed out"
                logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out. Retrying...")
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
    app.run(debug=True, host='0.0.0.0', port=5000)