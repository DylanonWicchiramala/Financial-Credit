import os
import utils
from langchain_core.messages import (
    AIMessage, 
    HumanMessage,
)
from datetime import datetime, timedelta
import database

utils.load_env()

COLLECTION_NAME = "Chat History"

def insert(bot_message:str, human_message:str, user_id: str = "test"):
    client, db = database.load_db()
    history = db[COLLECTION_NAME]

    timestamp = datetime.now()

    # Update the document in MongoDB
    history.update_one(
        {"user_id": user_id},
        {"$push": {
            "chat_history": {
                "$each": [
                    {"content": human_message, "timestamp": timestamp},
                    {"content": bot_message, "timestamp": timestamp}
                ]
            }
        }},
        upsert=True  # Create a new document if no matching document is found
    )
    
    client.close()
    return get(user_id=user_id)
    
    
def get(user_id:str="test", chat_history:list=[]):
    client, db = database.load_db()
    history = db[COLLECTION_NAME]
    
    query = history.find_one({"user_id": user_id})
    if query is None:
        query = {
            "user_id": user_id,
            "chat_history": [],
        }
        history.insert_one(query)

    for i, msg in enumerate(query["chat_history"]):
        msg = msg['content']
        chat_history.append(
            AIMessage(msg) if i % 2 == 1 else HumanMessage(msg)
        )
    
    client.close()
    return chat_history


def get_str(user_id:str="test", chat_history:list=[]):
    client, db = database.load_db()
    history = db[COLLECTION_NAME]

    query = history.find_one({"user_id": user_id})

    if query:
        for i, msg in enumerate(query["chat_history"]):
            msg = msg['content']
            chat_history.append(
                "Bot: " + msg if i % 2 == 1 else "Human: " + msg
            )

    client.close()
    return chat_history


def delete(user_id=None, time_before=None, delete_all=False):
    """
    Deletes chat history from the MongoDB collection.

    Parameters:
    - user_id (str, optional): The user_id whose chat history should be deleted.
    - time_before (datetime, optional): Deletes chat history before this datetime.
    - delete_all (bool, optional): If True, deletes all chat history for the user.

    Returns:
    - UpdateMany: The result of the update operation.
    """
    client, db = database.load_db()
    history = db[COLLECTION_NAME]
    query = {}

    # If deleting all chat history for a specific user or all users
    if delete_all:
        if user_id:
            query = {'user_id': user_id}
        else:
            query = {}

        # Remove entire chat history field
        return history.update_many(query, {'$unset': {'chat_history': 1}})

    # If filtering by user and time_before
    if user_id:
        query['user_id'] = user_id

    if time_before:
        query['chat_history.timestamp'] = {'$lt': time_before}
        # Remove specific entries from the chat history array based on the timestamp
        return history.update_many(query, {'$pull': {'chat_history': {'timestamp': {'$lt': time_before}}}})
    
    res = history.delete_many(query)  # Delete documents matching the query
    client.close()
    return res


# delete chat history older than 30 days.
# delete_chat_history(time_before=datetime.now() - timedelta(days=14))
# delete_chat_history(user_id="test", time_before=datetime.now() - timedelta(days=1))