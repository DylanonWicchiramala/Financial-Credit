# load env ------------------------------------------------------------------------
import os
import database.chat_history
import database.customer
import utils
import re

utils.load_env()
os.environ['LANGCHAIN_TRACING_V2'] = "false"


# debug ------------------------------------------------------------------
from langchain.globals import set_debug, set_verbose
set_verbose(False)
set_debug(False)

from langchain_core.messages import (
    HumanMessage,
)
from langgraph.graph import END, StateGraph, START
from agents import(
    AgentState,
    agents_metadata,
    agent_names
)
from langgraph.checkpoint.memory import MemorySaver

from tools import get_tools_output, all_tools, set_current_user_id
import database
## Define Tool Node
from langgraph.prebuilt import ToolNode
from typing import Literal

tool_node = ToolNode(all_tools)

def router(state) -> Literal["call_tool", "continue", "__end__"]:
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if "FINALANSWER" in last_message.content:
        return "__end__"
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    else:
        return "continue"


## Workflow Graph ------------------------------------------------------------------------
workflow = StateGraph(AgentState)

# add agent nodes
for name, value in agents_metadata.items():
    workflow.add_node(name, value['node'])
    
workflow.add_node("call_tool", tool_node)

workflow.add_conditional_edges(
    "service",
    router,
    {
        "call_tool": "call_tool",
        "__end__": END,
        "continue": END, 
        }
)

workflow.add_conditional_edges(
    "call_tool",
    # Each agent node updates the 'sender' field
    # the tool calling node does not, meaning
    # this edge will route back to the original agent
    # who invoked the tool
    lambda x: x["sender"],
    {name:name for name in agent_names},
)

workflow.add_edge(START, "service")
graph = workflow.compile()

def submitUserMessage(
    user_input:str, 
    user_id:str="test", 
    keep_chat_history:bool=False, 
    return_reference:bool=False, 
    verbose:bool=False,
    recursion_limit:int=20
    ) -> str:
    # set_current_user_id(user_id)
    chat_history = database.chat_history.get(user_id=user_id) if keep_chat_history else []
    chat_history = chat_history[-8:]
    
    # memory only keep chat history only along agents.
    # internal_level_memory = MemorySaver()
    # graph = workflow.compile(checkpointer=internal_level_memory)
    
    graph = workflow.compile()

    events = graph.stream(
        {
            "messages": [
                HumanMessage(
                    user_input
                )
            ],
            "chat_history": chat_history
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": recursion_limit, "thread_id":"a"},
    )
    
    if not verbose:
        events = [e for e in events]
        response = list(events[-1].values())[0]
    else:
        for e in events:
            a = list(e.items())[0]
            a[1]['messages'][0].pretty_print()
        
        response = a[1]
    
    response = response["messages"][0].content
    response = utils.format_bot_response(response, markdown=True)
    
    if keep_chat_history:
        chat_history = database.chat_history.insert(bot_message=response, human_message=user_input, user_id=user_id)
    
    if return_reference:
        return response, get_tools_output()
    else:
        return response
    
    
def submitUserMessageWithDebugCommand(*arg, **kwargs) -> str:
    user_input = arg[0]
    
    if re.search(r"//delete chat history", user_input):
        o = database.chat_history.delete(user_id=kwargs['user_id'])
        return f"chat history of this user have been deleted."
        
    if re.search(r"//reset", user_input):
        database.customer.delete(user_id="test")
        database.chat_history.delete(user_id=kwargs['user_id'])
        database.customer.update({
            "name":"สมชาย สายชม",
        },user_id=kwargs['user_id'])
        return f"user data and chat history have been reset."
    
    if re.search(r"//get chat history", user_input):
        history = database.chat_history.get_str(user_id=kwargs['user_id'])
        nl = "\n"
        return f"chat history: \n{nl.join(history)}"
        
    if re.search(r"//get user data", user_input):
        user_data = database.customer.get(user_id=kwargs['user_id'])
        return f"user data: \n{user_data}"
    
    if re.search(r"//chat history ?= ?true", user_input):
        user_input = re.sub(r"//chat history ?= ?(true|false)", '', user_input)
        kwargs['keep_chat_history'] = True
        
    if re.search(r"//chat history ?= ?false", user_input):
        user_input = re.sub(r"//chat history ?= ?(true|false)", '', user_input)
        kwargs['keep_chat_history'] = False
        
    if re.search(r"//debug", user_input):
        user_input = re.sub(r"\debug", '', user_input)
        kwargs['verbose'] = True
        try:
            return submitUserMessage(*arg,*kwargs)
        except Exception as e:
            return f"error: {e}"
        
        
    return submitUserMessage(*arg,**kwargs)