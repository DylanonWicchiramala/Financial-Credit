# %%
import json
import requests
import os
import utils
import uuid

utils.load_env()

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_TOKEN")
CHANNEL_SECRET = os.environ.get("LINE_SECRET")
BOT_VERBOSE = int(os.environ['BOT_VERBOSE'])


def ReplyMessage(reply_token, TextMessage:list|str):
    LINE_API = 'https://api.line.me/v2/bot/message/reply'
    Authorization = f'Bearer {CHANNEL_ACCESS_TOKEN}'    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization
    }
    # remove * and # in message
    answer = TextMessage
    
    if isinstance(answer, str):
        data = {
            "replyToken": reply_token,
            "messages": [
                {
                "type": "text",
                "text": answer,
                },
            ]
        }
    elif len(answer)<=5:
        data = {
            "replyToken": reply_token,
            "messages": [
                {
                "type": "text",
                "text": ans,
                } for ans in answer
            ]
        }
    elif len(answer)>5:
        raise ValueError("List of TextMessage must have length less than 5")
    
    # Convert the dictionary to a JSON string
    data = json.dumps(data)
    
    # Send the POST request to the LINE API
    response = requests.post(LINE_API, headers=headers, data=data)
    
    return response
    

def PushMessage(user_id:str, TextMessage:list|str):

    # Define the endpoint URL
    LINE_API = "https://api.line.me/v2/bot/message/push"
    Authorization = f'Bearer {CHANNEL_ACCESS_TOKEN}' 

    # Define the headers
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization,
        'X-Line-Retry-Key': str(uuid.uuid4())  # Generate a unique UUID
    }

    # Define the payload (data to send in the POST request)
    if isinstance(TextMessage, str):
        data = {
            "to": user_id,  # Replace with the target user ID
            "messages": [
                {
                    "type": "text",
                    "text": TextMessage
                }
            ]
        }
    elif len(TextMessage)<=5:
        data = {
            "to": user_id,  # Replace with the target user ID
            "messages": [
                {
                    "type": "text",
                    "text": message
                }for message in TextMessage
            ]
        }
    elif len(TextMessage)>5:
        raise ValueError("List of TextMessage must have length less than 5")

    # Send the POST request
    response = requests.post(LINE_API, headers=headers, json=data)

    return response