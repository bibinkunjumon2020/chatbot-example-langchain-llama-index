# main.py
"""
Interactive chat with memory for earlier chats.
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin  # Setting cors for http
from tele_bot import load_query_engine, construct_index
import logging

# Create a Flask app
chat_app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for the app
cors = CORS(chat_app)  # Setting cors for http
chat_app.config["CORS_HEADERS"] = "Content-Type"  

"""
Method for handling user chat api calls # Define an API route for handling user text input
"""
@chat_app.route("/api/send_text", methods=["POST"])
@cross_origin()  # Setting cors for http
def send_text():
    try:
        message_response="Server Error or Usage Limit"# To avoid HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out
        data = request.get_json()
        input_text = (
            data.get("text", "hi") + "?"
        )  # if no text in json,add 'hi' and add '?' to make proper conversation answer.
        # Load the chat engine
        chat_engine = load_query_engine()
        if chat_engine is not None:
            response = chat_engine.query(input_text)
            if response is not None: 
                message_response = f"{response.response}"
                if len(message_response) == 0:
                    message_response = "Sorry, no response could be generated."
        else:
            return jsonify({"response": "Inconvenience Regretted! Chatbot is not responding at the moment."})
    except Exception as e:
        logging.error("error occurred while generating the response"+e)
        message_response = "Sorry, an error occurred while generating the response.\n"+ e
    finally:
        return jsonify({"response": message_response})

"""
api call for resetting the chat # Define an API route for resetting the chat (if needed)
"""
@chat_app.route('/api/chat_reset', methods=['POST'])
@cross_origin() # Setting cors for http
def chat_reset():
    try:
        # chat_engine = get_chat_engine()
        # chat_engine.reset()
        response = make_response('Chat Resetted',200)
        return response
    except Exception as e:
        return jsonify({"response": str(e)}), 500

# Run the Flask app if this script is the main entry point
if __name__ == "__main__":
    # construct_index()
    chat_app.run(host="0.0.0.0", port=5000)

