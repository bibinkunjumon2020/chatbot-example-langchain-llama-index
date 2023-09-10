#main.py 
"""
Interactive chat with memory for earlier chats.
"""
from flask import Flask, request, jsonify,make_response
from index_handler import load_index,store_index
from flask_cors import CORS, cross_origin # Setting cors for http
from llama_index.memory import ChatMemoryBuffer
from llama_index.llms import ChatMessage,MessageRole


chat_app = Flask(__name__)
cors = CORS(chat_app) # Setting cors for http
chat_app.config['CORS_HEADERS'] = 'Content-Type' # Setting cors for http
messages = []
"""
Method for handling user chat api calls
"""
@chat_app.route('/api/send_text', methods=['POST'])
@cross_origin() # Setting cors for http
def send_text(): 
    data = request.get_json()
    input_text = data.get('text', 'hi')+'?' # if no text in json,add 'hi' and add '?' to make proper conversation answer.
    # chat_engine = get_chat_engine() 
    index = load_index()
    chat_engine = index.as_chat_engine(chat_mode="condense_question")
    ####
    query_engine = index.as_query_engine()
    query_engine.query()

    ###
    messages.append(ChatMessage(role=MessageRole.SYSTEM,content="You are a chatbot with knowledge limited \
                                to the content of the indexed documents.Please provide answers and information \
                                based only on the content within those documents."))
    messages.append(ChatMessage(role="user", content=input_text))

    response = chat_engine.chat(message="Only answer from the context,"+input_text,chat_history=messages)
    messages.append(ChatMessage(role=MessageRole.ASSISTANT,content=f"{response}"))
    return jsonify({'response': f"{response}"})

"""
api call for resetting the chat
"""
@chat_app.route('/api/chat_reset', methods=['POST'])
@cross_origin() # Setting cors for http
def chat_reset():
    chat_engine = get_chat_engine()
    chat_engine.reset()
    response = make_response('Chat Resetted',200)
    print("chat resetted")
    return response

"""
Method for loading the index file and initializing the chat_engine
"""
def get_chat_engine():
    if not hasattr(chat_app, 'chat_engine'):
        index = load_index()  # Load your index using your custom function
        memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
        chat_engine = index.as_chat_engine(
            chat_mode="openai",
            memory=memory,
            system_prompt = "You are a chatbot with knowledge limited to the content of the indexed documents. \
                Please provide answers and information based only on the content within those documents."
        )
        chat_app.chat_engine = chat_engine  # Store chat_engine in the app context
    return chat_app.chat_engine

if __name__ == '__main__':
    # store_index()
    chat_app.run(host='0.0.0.0', port=5000)

# import asyncio

# chat_app = Flask(__name__)

# @chat_app.route('/api/send_text', methods=['POST'])
# @cross_origin() # Setting cors for http
# def send_text(): 
#     # Create and set an event loop for the current thread
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)

#     data = request.get_json()
#     input_text = data.get('text', 'hi')+'?' # if no text in json,add 'hi' and add '?' to make proper conversation answer.
#     chat_engine = get_chat_engine() 
#     response = chat_engine.stream_chat(input_text)
#     for token in response.response_gen:
#         print(token)


