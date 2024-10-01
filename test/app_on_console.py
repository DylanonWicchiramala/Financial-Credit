# append project work dir path
from os.path import dirname, realpath, sep, pardir
import sys
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

from utils import notify
import requests
from time import time
from chatbot_multiagent import AgentBot

Bot = AgentBot(keep_chat_history=True, verbose=True)

# url = "https://market-feasibility-analysis-chatbot-2-jelvbvjqna-uc.a.run.app/test"
url = "http://127.0.0.1:8080/test"


def api_request(message, url_endpoint:str=url):
    headers = {"Content-Type": "application/json"}
    data = {"message": message}

    response = requests.post(url_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        notify("purr")
        return(response.json().get("response"))
    else:
        notify("hero")
        return("Error:", response.json())


while True:
    message = input("Human: ")
    stt = time()
    
    # bot_message = api_request(message=message)
    bot_message = Bot.submit_user_message_with_debug_command(message, user_id="test")
    print("Bot meassage: ", bot_message)
    
    # print(f"process exetcution time {round(time()-stt,2)} sec.")