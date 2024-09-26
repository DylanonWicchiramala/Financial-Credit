import time
from chatbot_multiagent import submitUserMessage, submitUserMessageWithDebugCommand

while True:
    message = input("Human: ")
    bot_message = submitUserMessageWithDebugCommand(message, user_id="test", keep_chat_history=True, verbose=False)
    print("Bot meassage: ", bot_message)