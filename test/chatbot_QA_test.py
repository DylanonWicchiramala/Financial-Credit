# %%
# append project work dir path
import functools
from os.path import dirname, realpath, sep, pardir
import sys

import tqdm
sys.path.append(dirname(realpath(__file__)) + sep + pardir)

from chatbot_multiagent import submitUserMessage
import requests
import random
from math import inf
from time import time, sleep
import utils

def save_test_result(test_result, path:str = 'test/testset/QA_test_result.txt'):
    results, exet_rept = test_result
    # Open the file in write mode
    with open(path, 'w') as file:
    # Iterate over each dictionary in the list
        for result in results:
        # Iterate over each key-value pair in the dictionary
            for key, value in result.items():
            # Write each key-value pair to the file
                file.write(f"{key}: \n\t{str(value).strip()}\n")
        # Add a blank line between dictionaries
            file.write("\n\n")
            file.write("-"*200+"\n")
    
        file.write(exet_rept)

    print(f"Results saved to {path}")
    
    
def append_test_result(test_result: dict, path: str = 'test/testset/QA_test_result.txt'):
    """Appends test results to the specified text file.

    Args:
        result (dict): Dictionary containing 'quesion' and 'answer' (or 'error') fields.
        result_save_path (str): Path to the file where the results should be saved.
    """
    # Open the file in append mode to add new results at the end of the file
    with open(path, 'a', encoding='utf-8') as file:
        # Format the result as a string to save
        for key, value in test_result.items():
            file.write(f"{key}: \n\t{str(value).strip()}\n")
        
        file.write("\n\n")
        file.write("-"*200+"\n")

    print(f"Append result to {path}")


def QA_sample_test(quesion_test:list[str], result_save_path='test/testset/QA_test_result.txt', num_samples:int=inf):
    stt = time()
    # Ensure there are at least 5 lines in the list
    num_samples = min(num_samples, len(quesion_test))
    sample_quesion = random.sample(quesion_test, num_samples)
    
    __append_test_result = functools.partial(append_test_result, path=result_save_path)
        
    result = []
    for quesion in tqdm(sample_quesion):
        print("Question: ", quesion.strip())
        try:
            answer = submitUserMessage(quesion, keep_chat_history=False)
            print("Response: ", answer[:100].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'answer': answer})   
            __append_test_result({'quesion': quesion, 'answer': answer})
        except Exception as e:
            result.append({'quesion': quesion, 'error': e}) 
            __append_test_result({'quesion': quesion, 'error': e})
            print("Error: ", str(e)[:1000].replace("\n", " "), "...")
        
    exet = time() - stt
    exet_rept = f"{exet/num_samples} sec."
    print(exet_rept)
    
    __append_test_result({'average execution time': exet_rept})
    return result, exet_rept


def API_test(quesion_test:list[str], result_save_path='test/testset/api_QA_test_result.txt', num_samples:int=inf, endpoint="https://market-feasibility-analysis-chatbot-2-jelvbvjqna-uc.a.run.app/test"):
    stt = time()
    # Ensure there are at least 5 lines in the list
    num_samples = min(num_samples, len(quesion_test))
    sample_quesion = random.sample(quesion_test, num_samples)
    
    __append_test_result = functools.partial(append_test_result, path=result_save_path)
    
    result = []
    for quesion in tqdm(sample_quesion):
        headers = {"Content-Type": "application/json"}
        data = {"message": quesion}
        print("Question: ", quesion.strip())

        sleep(1)
        response = requests.post(endpoint, json=data, headers=headers)

        if response.status_code == 200:
            answer = response.json().get("response")
            print("Response ", response.status_code, ": ", answer[:100].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'answer': answer})   
            __append_test_result({'quesion': quesion, 'answer': answer})
        else:
            err_massage = response.json().get("error")
            print("Error ", response.status_code, ": ", err_massage[:1000].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'error': err_massage}) 
            __append_test_result({'quesion': quesion, 'error': err_massage})
            
    exet = time() - stt
    exet_rept = f"{exet/num_samples} sec."
    print(exet_rept)
    
    __append_test_result({'average execution time': exet_rept})
    return result, exet_rept

# %%
with open('./test/testset/user_question_testsets.txt', 'r') as file:
    quesion_test = file.readlines()    

endpoint="https://market-feasibility-analysis-chatbot-212399072243.asia-east1.run.app/test"
# endpoint="http://127.0.0.1:8080/test"

# results, exet_rept = API_test(quesion_test, num_samples=8, result_save_path='test/testset/api_QA_test_result.txt', endpoint=endpoint); utils.notify("aurora")
results, exet_rept = QA_sample_test(quesion_test, num_samples=10, result_save_path="test/testset/QA_test_result.txt"); utils.notify("aurora")
