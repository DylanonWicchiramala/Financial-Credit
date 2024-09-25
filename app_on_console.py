import time
from chatbot_multiagent import submitUserMessage

import database
import database.chat_history

database.chat_history.delete(user_id="test")

while True:
    message = input("Human: ")
    bot_message = submitUserMessage(message, user_id="test", keep_chat_history=True, return_reference=False, verbose=True)
    print("Bot meassage: ", bot_message)