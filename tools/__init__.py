# %%
## Document vector store for context
from langchain_core.tools import tool
import functools
from copy import copy

from typing import TypedDict, Optional, NotRequired, Literal
import database
import database.customer

tools_outputs=""
CURRENT_USER_ID: str = "test"


def get_tools_output():
    global tools_outputs
    result = copy(tools_outputs)
    tools_outputs = ""
    return result


def save_tools_output(func):
    @functools.wraps(func) 
    def wrapper(*args, **kwargs):
        global tools_outputs
        # Call the original function and get its return value
        result = func(*args, **kwargs)
        # Append the result to tools_outputs
        tools_outputs += str(result) + "\n"
        # Return the original result
        return result
    return wrapper


def set_current_user_id(user_id:str):
    global CURRENT_USER_ID
    CURRENT_USER_ID = user_id


class CustomerInput(TypedDict):
    age: NotRequired[int]
    income_source: NotRequired[list[Literal["employment", "business", "investment", "freelance", "rental","gifts or financial support", "none"]]]
    monthly_income: NotRequired[int]
    outstanding_loan_amount: NotRequired[int]
    loan_history: NotRequired[Literal['ever', 'never']]
    missed_payments: NotRequired[Literal['ever', 'never']]
    total_debt_payment_monthly: NotRequired[int]
    payment_types: NotRequired[str]
    significant_assets: NotRequired[str]


def set_customer_data(input:CustomerInput):
    """ set a customer personal data and credit data contain. function will return updatted customers data
    user_id: str 
    age: age of customer in intreger
    income_source: sources of income of customer. list of string of income sources 
    monthly_income: total average customer income monthly in intreger in baht
    outstanding_loan_amount: customer curent total loan left to paid. (such as mortgages, personal loans, car loans)
    loan_history: Is customer ever have a loan.
    missed_payments: Is customer ever missed or delayed payments.
    total_debt_payment_monthly: total expenses from debt in month.
    payment_types: what kind of debt their paid. car, realestate, credit card
    significant_assets: asset customer have such as house, car.
    """
    global CURRENT_USER_ID
    user_id = CURRENT_USER_ID
    
    customer_data = database.customer.get(user_id=user_id.strip())
    
    customer_data.update(input)
    
    # if customer no income
    if customer_data.get("income_source")==['none'] or customer_data.get("monthly_income",-1)==0:
        customer_data["income_source"] = ['none']
        customer_data["monthly_income"] = 0
    
    # no current loan
    if customer_data.get("outstanding_loan_amount",-1)==0 or customer_data.get("total_debt_payment_monthly",-1)==0:
        customer_data["outstanding_loan_amount"] = 0
        customer_data["total_debt_payment_monthly"] = 0
    
    # never have loan
    if customer_data.get("loan_history")=='never':
        customer_data["missed_payments"] = 'never'
        customer_data["outstanding_loan_amount"] = 0
        customer_data["total_debt_payment_monthly"] = 0
        
    
    return database.customer.update(user_id=user_id, data=customer_data)
    
    
def get_customer_data():
    """ this function to get customer personal data and credit data contain
    """
    global CURRENT_USER_ID
    user_id = CURRENT_USER_ID
    data_fields = [
        "age",
        "income_source",
        "monthly_income",
        "outstanding_loan_amount",
        "loan_history",
        "missed_payments",
        "total_debt_payment_monthly",
        "payment_types",
        "significant_assets",
    ]
    customer_data = CustomerInput(database.customer.get(user_id=user_id.strip()))
    for key in data_fields:
        customer_data[key] = customer_data.get(key, None)
    return customer_data


set_customer_data = tool(set_customer_data)
get_customer_data = tool(get_customer_data)

all_tools = [
    set_customer_data,
    get_customer_data,
    ]

tools = {tool.name: tool for tool in all_tools}