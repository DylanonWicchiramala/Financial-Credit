import time
from chatbot_multiagent import submitUserMessage

while True:
    message = input("Human: ")
    bot_message = submitUserMessage(message, user_id="example", keep_chat_history=True, return_reference=False, verbose=False)
    print("Bot meassage: ", bot_message)