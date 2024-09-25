from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import utils
import os

def load_db():
    utils.load_env()
    
    # Load MongoDB credentials and set up the connection
    mongo = os.environ.get('MONGODB_PASS')
    uri = f"mongodb+srv://dylan:{mongo}@cluster0.wl8mbpy.mongodb.net/"
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client["FinancialCredit"]
    
    return client, db