import time
from chatbot_multiagent import submitUserMessageWithDebugCommand

# submitUserMessageWithDebugCommand("/", user_id="test", keep_chat_history=True, verbose=False)

while True:
    message = input("Human: ")
    bot_message = submitUserMessageWithDebugCommand(message, user_id="test", keep_chat_history=True, verbose=True)
    print("Bot meassage: ", bot_message)