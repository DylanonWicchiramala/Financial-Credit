# %%
# append project work dir path
from os.path import dirname, realpath, sep, pardir
import sys
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


def QA_sample_test(quesion_test:list[str], result_save_path='test/testset/QA_test_result.txt', num_samples:int=inf):
    stt = time()
    # Ensure there are at least 5 lines in the list
    num_samples = min(num_samples, len(quesion_test))
    sample_quesion = random.sample(quesion_test, num_samples)
        
    result = []
    for quesion in sample_quesion:
        try:
            answer = submitUserMessage(quesion, keep_chat_history=True)
            print("Response: ", answer[:100].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'answer': answer})   
        except Exception as e:
            result.append({'quesion': quesion, 'error': e}) 
            print("Error: ", str(e)[:1000].replace("\n", " "), "...")
        
    exet = time() - stt
    exet_rept = f"average execution time: {exet/num_samples}sec."
    print(exet_rept)
    
    save_test_result((result, exet_rept), result_save_path)
    return result, exet_rept


def API_test(quesion_test:list[str], result_save_path='test/testset/api_QA_test_result.txt', num_samples:int=inf, endpoint="https://market-feasibility-analysis-chatbot-2-jelvbvjqna-uc.a.run.app/test"):
    stt = time()
    # Ensure there are at least 5 lines in the list
    num_samples = min(num_samples, len(quesion_test))
    sample_quesion = random.sample(quesion_test, num_samples)
    
    result = []
    for quesion in sample_quesion:
        headers = {"Content-Type": "application/json"}
        data = {"message": quesion}

        sleep(1)
        response = requests.post(endpoint, json=data, headers=headers)

        if response.status_code == 200:
            answer = response.json().get("response")
            print("Response ", response.status_code, ": ", answer[:100].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'answer': answer})   
        else:
            err_massage = response.json().get("error")
            print("Error ", response.status_code, ": ", err_massage[:1000].replace("\n", " "), "...")
            result.append({'quesion': quesion, 'error': err_massage}) 
            
    exet = time() - stt
    exet_rept = f"average execution time: {exet/num_samples}sec."
    print(exet_rept)
    
    save_test_result((result, exet_rept), result_save_path)
    return result, exet_rept

# %%
with open('./test/testset/user_question_testsets.txt', 'r') as file:
    quesion_test = file.readlines()    

endpoint="https://retail-store-chatbot-212399072243.asia-east1.run.app/test"
# endpoint="http://127.0.0.1:8080/test"

results, exet_rept = QA_sample_test(quesion_test, num_samples=10, result_save_path="test/testset/QA_test_result.txt"); utils.notify("aurora")
# results, exet_rept = API_test(quesion_test, num_samples=10, result_save_path='test/testset/api_QA_test_result.txt', endpoint=endpoint); utils.notify("aurora")