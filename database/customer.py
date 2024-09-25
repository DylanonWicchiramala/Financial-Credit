import os
import utils
from langchain_core.messages import (
    AIMessage, 
    HumanMessage,
)
from datetime import datetime, timedelta
import database
from typing import TypedDict, Optional, NotRequired, Literal

utils.load_env()

COLLECTION_NAME = "Customer"

class InputSchema(TypedDict):
    name: NotRequired[str]
    age: NotRequired[int]
    income_source: NotRequired[list[Literal["employment", "business", "investment", "freelance", "rental"]]]
    monthly_income: NotRequired[int]
    job_status: NotRequired[Literal["employed", "self-employed", "unemployed"]]
    outstanding_loan_amount: NotRequired[int]
    loan_history: NotRequired[Literal['ever', 'never']]
    missed_payments: NotRequired[Literal['ever', 'never']]
    total_debt_payment_monthly: NotRequired[int]
    payment_types: NotRequired[str]
    significant_assets: NotRequired[str]
        

def update(data: InputSchema, user_id: str = "test"):
    client, db = database.load_db()
    customer = db[COLLECTION_NAME]

    # Update or create the document in MongoDB
    customer.update_one(
        {"user_id": user_id},  # Filter by user_id
        {"$set": data},        # Use $set to update the fields
        upsert=True            # Create a new document if no matching document is found
    )

    client.close()
    return get(user_id=user_id)
    
    
def get(user_id:str="test"):
    client, db = database.load_db()
    customer = db[COLLECTION_NAME]
    
    query = customer.find_one({"user_id": user_id})
    
    client.close()
    return query


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