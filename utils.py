from dotenv import load_dotenv as __load_dotenv
import os
import json
import functools
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from typing import Any, List, Union, Tuple, Literal

sound_effects = {
    "blow" : "/System/Library/Sounds/blow.aiff",
    "glass" : "/System/Library/Sounds/glass.aiff",
    "hero" : "/System/Library/Sounds/Hero.aiff",
    "basso" : "/System/Library/Sounds/basso.aiff",
    "bottle" : "/System/Library/Sounds/bottle.aiff",
    "frog" : "/System/Library/Sounds/frog.aiff",
    "funk" : "/System/Library/Sounds/funk.aiff",
    "morse" : "/System/Library/Sounds/morse.aiff",
    "ping" : "/System/Library/Sounds/ping.aiff",
    "pop" : "/System/Library/Sounds/pop.aiff",
    "purr" : "/System/Library/Sounds/purr.aiff",
    "sosumi" : "/System/Library/Sounds/sosumi.aiff",
    "submarine" : "/System/Library/Sounds/submarine.aiff",
    "tink" : "/System/Library/Sounds/tink.aiff",
    "aurora" : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Modern/Aurora.m4r",
    "Alert".lower() : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Classic/Alert.m4r",
    "Anticipate".lower() : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Classic/Anticipate.m4r",
    "Apex".lower() : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/Ringtones/Apex.m4r",
    "chord" : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Modern/Chord.m4r",
    "note" : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Modern/Note.m4r",
    "".lower() : "/System/Library/PrivateFrameworks/ToneLibrary.framework/Versions/A/Resources/AlertTones/Modern/Aurora.m4r",
}

def notify(
    sound_effect:Literal["blow", "glass", "hero", "basso", "bottle", "frog", "funk", "morse", "ping", "pop", "purr", "sosumi", "submarine", "tink", "aurora", "alert", "anticipate", "apex", "chord", "note"]="aurora", 
    notification_description:str="notified."):
    """ get macos notification.
    sound_effect: blow, glass, hero, basso, bottle, frog, funk, morse, ping, pop, purr, sosumi, submarine, tink, aurora, Alert, Anticipate, Apex, chord, note
    """
    try: 
        os.system('afplay '+ sound_effects[sound_effect.lower()])
    except:
        print(notification_description)


def notify_process(func, sound_effect:Literal["blow", "glass", "hero", "basso", "bottle", "frog", "funk", "morse", "ping", "pop", "purr", "sosumi", "submarine", "tink", "aurora", "alert", "anticipate", "apex", "chord", "note"]="aurora"):
    """ get macos notify when wrapped function complete.
    sound_effect: blow, glass, hero, basso, bottle, frog, funk, morse, ping, pop, purr, sosumi, submarine, tink, aurora, Alert, Anticipate, Apex, chord, note
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        notify(sound_effect, f"function {func.__name__} process completed.")
        return output
    
    return wrapper


def bundle_input(func):
    """ decorator function designed to handle both single objects and collections (lists or tuples) as input. It allows a function to be applied to either an individual item or each item in a list/tuple, returning a corresponding list of results when a collection is provided.
    """
    @functools.wraps(func)  # Preserve the original function's metadata
    def wrapper(input: Union[Any, List[Any], Tuple[Any]], *args, **kwargs):
        
        # Check if the input is a list
        if isinstance(input, list) or isinstance(input, tuple):
            # Apply the function to each item in the list
            results = [func(item, *args, **kwargs) for item in input]
            return results
        else:
            # Apply the function to the single input object
            result = func(input, *args, **kwargs)
            return result

    return wrapper


# move to database
# def load_project_db():
#     load_env()
    
#     # Load MongoDB credentials and set up the connection
#     mongo = os.environ.get('MONGODB_PASS')
#     uri = f"mongodb+srv://dylan:{mongo}@cluster0.wl8mbpy.mongodb.net/"
#     client = MongoClient(uri, server_api=ServerApi('1'))

#     # Connect to the "RetailStore" database
#     db = client["RetailStore"]
    
#     return client, db


def load_agent_meta():
    with open('./prompt.json', 'r') as file:
        prompt_data = json.load(file)
    return prompt_data


def load_env():
    # Load environment variables from the .env file
    return __load_dotenv("./.env") 
    
    
@bundle_input 
def remove_markdown(text:str):
    md_symbol = "#*"
    for sym in md_symbol:
        text = text.replace(sym,"")
    
    return text


@bundle_input
def strip(text:str):
    return text.strip()


@bundle_input
def format_bot_response(text:str, markdown:bool=True):
    text = text.replace("FINALANSWER:", "")
    text = text.replace("FINALANSWER,", "")
    text = text.replace("FINALANSWER", "")
    text = remove_markdown(text) if not markdown else text
    text = strip(text)
    return text