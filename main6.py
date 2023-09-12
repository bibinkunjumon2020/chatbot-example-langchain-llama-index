# main.py
"""
Interactive chat with memory for earlier chats.
"""
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin  # Setting cors for http
from index_handler import load_index
from llama_index.memory import ChatMemoryBuffer
import logging
import asyncio
import threading

# Create a Flask app
chat_app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for the app
cors = CORS(chat_app)  # Setting cors for http
chat_app.config["CORS_HEADERS"] = "Content-Type"
# logging.basicConfig(level=logging.DEBUG)


# Define a function to run in a thread
def handle_chat_thread(chat_engine,input_text): 
    global text_completion
    text_completion = chat_engine.chat("Only answer from the context," + input_text)

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
            #making a thread for handling openai chat calls
            chat_thread = threading.Thread(target=handle_chat_thread,kwargs={"chat_engine":chat_engine,"input_text":input_text})
            chat_thread.start()
            #main thread waiting for chat_thread completion
            chat_thread.join()
            #assigning the value created by chat_thread
            if text_completion is not None:
                message_response = f"{text_completion}"
                if len(message_response) == 0:
                    message_response = "Inconvenience Regretted!\nNo response could be generated..!"
        else:#when chat_enine not exist or None
            #creating a new chat_engine
            asyncio.run(get_chat_engine())
            message_response = (
                "Chatbot is Ready..!\nTry again"
            )
            logging.error(
                 "Chat engine was missing - Recreated."
            )

    except Exception as e:
        logging.error("Exception occurred while generating the response - " + str(e))
        message_response = "Inconvenience Regretted!\nAn Exception occurred while generating the response."
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
        response = "Chat Resetted"
    else:#when chat_enine not exist or None
        #creating a new chat_engine
        asyncio.run(get_chat_engine())
        response = (
             "Chatbot is Ready..!"
        )
        logging.error( "Chatbot is Ready..!")

    return make_response(response, 200)


"""
Method for loading the index file and initializing the chat_engine with memory
"""


async def get_chat_engine():
    logging.info(" Inside method get_chat_engine ")
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
    asyncio.run(get_chat_engine())
    chat_app.run(host="0.0.0.0", port=5000)
