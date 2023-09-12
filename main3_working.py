# main.py
"""
Interactive chat with memory for earlier chats.
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin  # Setting cors for http
from index_handler import load_index
from llama_index.memory import ChatMemoryBuffer
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
        message_response = "Server Error or Usage Limit"  # To avoid HTTPSConnectionPool(host='api.openai.com', port=443): Read timed out
        data = request.get_json()
        input_text = (
            data.get("text", "hi") + "?"
        )  # if no text in json,add 'hi' and add '?' to make proper conversation answer.
        # Load the chat engine
        if hasattr(chat_app, "chat_engine") and chat_app.chat_engine is not None:
            chat_engine = chat_app.chat_engine
            response = chat_engine.chat("Only answer from the context," + input_text)
            if response is not None:
                message_response = f"{response}"
                if len(message_response) == 0:
                    message_response = "Sorry, no response could be generated."
        else:
            message_response = (
                "Inconvenience Regretted! Chatbot is not responding at the moment."
            )
            logging.error("Chatbot chat_engine is missing")

    except Exception as e:
        logging.error("Error occurred while generating the response - " + str(e))
        message_response = (
            "Sorry, an error occurred while generating the response."
        )
    finally:
        return jsonify({"response": message_response})


"""
api call for resetting the chat # Define an API route for resetting the chat (if needed)
"""


@chat_app.route("/api/chat_reset", methods=["POST"])
@cross_origin()  # Setting cors for http
def chat_reset():
    if hasattr(chat_app, "chat_engine") and chat_app.chat_engine is not None:
        chat_app.chat_engine.reset()
        response = make_response("Chat Resetted", 200)
    else:
        response = make_response("Chat engine missing", 404)

    return response


"""
Method for loading the index file and initializing the chat_engine with memory
"""


def get_chat_engine():
    if not hasattr(chat_app, "chat_engine"):
        index = load_index()  # Load your index using your custom function
        memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
        chat_engine = index.as_chat_engine(
            chat_mode="context",
            memory=memory,
            system_prompt="You are a chatbot with knowledge limited \
                                to the content of the indexed documents.Please provide answers and information \
                                based only on the content within those documents."
            # system_prompt="You are a chatbot, able to have normal interactions,from the document",
        )
        chat_app.chat_engine = chat_engine  # Store chat_engine in the app context


# Run the Flask app if this script is the main entry point
if __name__ == "__main__":
    # construct_index()
    get_chat_engine()
    chat_app.run(host="0.0.0.0", port=5000)
