import langchain_core
from langchain_core.messages import (
    AIMessage, 
    BaseMessage,
    ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import operator
from typing import Annotated, Sequence, TypedDict, List

from langchain_core.tools.structured import StructuredTool
from langchain_openai.chat_models.base import ChatOpenAI
from agents.prompt import (
    SYSTEM_PROMPT,
    SERVICE_PROMPT
)
from tools import (
    all_tools, 
    set_customer_data,
    CURRENT_USER_ID
)
import functools
import database.customer

## Define state ------------------------------------------------------------------------
# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history: List[BaseMessage]
    sender: str


def __get_customer_data()->dict:
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
    customer_data = database.customer.get(user_id=user_id.strip())
    for key in data_fields:
        customer_data[key] = customer_data.get(key, None)
    return customer_data


def __bind(llm, tools:list, agent_prompt:str):
    """ create llm with SYSTEM_PROMPT and agent prompt, bind tools, return LLM agent with tools and prompts.
    """
    ## create agents with prompt and tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=agent_prompt)
    prompt = prompt.partial(agent_names=agent_names)
    
    # return llm without tools
    if tools:
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        #llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])
        llm = llm.bind_tools(tools)
    else:
        prompt = prompt.partial(tool_names="<no available tools for you>")
    
    agent = prompt | llm
    return agent


def service_node_build(state:AgentState, name:str, tools:StructuredTool, llm:ChatOpenAI) -> AgentState:
    """ bulid `service` agent node to use in langgraph.
        use functools.partial to pass the argument `name`, `tools`, `llm`.
    """
    
    customer_data = str(__get_customer_data())
    
    prompt = SERVICE_PROMPT + "\nCustomer Data: " + customer_data
    
    agent = __bind(llm, tools, prompt)
    
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if not isinstance(result, ToolMessage):
        chat_history = state.get('chat_history')
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        "chat_history" : chat_history,
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


agent_names = ['service']

agent_nodes = {name:None for name in agent_names}

agent_nodes['service'] = functools.partial(service_node_build, name='service', tools=[set_customer_data])

# agent_nodes['service']({'chat_history':[], 'messages':[]})