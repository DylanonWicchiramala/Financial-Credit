# append project work dir path
from os.path import dirname, realpath, sep, pardir
import sys
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

from utils import notify
import requests
from time import time

url = "https://market-feasibility-analysis-chatbot-2-jelvbvjqna-uc.a.run.app/test"
# url = "http://127.0.0.1:8080/test"

headers = {"Content-Type": "application/json"}
data = {"message": "ทำ feasibility report เกี่ยวร้านเกมแถวสยาม"}

stt = time()
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Chatbot response:", response.json().get("response"))
    notify("purr")
else:
    print("Error:", response)
    notify("hero")

print(f"process exetcution time {round(time()-stt,2)} sec.")