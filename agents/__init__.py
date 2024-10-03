from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage, 
    BaseMessage,
    ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import operator
from typing import Annotated, Sequence, TypedDict, List
from agents.prompt import (
    SYSTEM_PROMPT,
    SERVICE_PROMPT
)
from tools import (
    all_tools, 
    set_customer_data,
    get_customer_data
)
import functools

## Define state ------------------------------------------------------------------------
# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history: List[BaseMessage]
    sender: str


def __bind(llm, tools:list, agnet_prompt:str):
    """ create llm with SYSTEM_PROMPT and agent prompt, bind tools, then return agent.
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
    prompt = prompt.partial(system_message=agnet_prompt)
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


def service_node_build(state:AgentState, name, tools, **llm_kwargs) -> AgentState:
    llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18", 
    temperature=0, 
    top_p=0, 
    **llm_kwargs
    )
    
    agent = __bind(llm, tools, SERVICE_PROMPT)
    
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

agent_nodes['service'] = functools.partial(service_node_build, name='service', tools=all_tools)

# agent_nodes['service']({'chat_history':[], 'messages':[]})