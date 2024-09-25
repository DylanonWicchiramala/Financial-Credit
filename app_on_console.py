import time
from chatbot_multiagent import submitUserMessage

while True:
    message = input("Human: ")
    bot_message = submitUserMessage(message, keep_chat_history=True, return_reference=False, verbose=False)
    print("Bot meassage: ", bot_message)