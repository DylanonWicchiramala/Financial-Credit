from langchain_openai import ChatOpenAI
from langchain_core.messages import (
    AIMessage, 
    BaseMessage,
    ToolMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import operator
from typing import Annotated, Sequence, TypedDict, List
from agents.metadata import (
    system_prompt,
    agents_metadata
)
import functools

llm = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18", 
    temperature=0, 
    top_p=0, 
    )

## Create agents ------------------------------------------------------------------------
def create_agent(llm, tools, system_message: str):
    # memory = ConversationBufferMemory(memory_key='chat_history', return_messages=False)
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
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


## create agent node
def agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        # result = AIMessage(**result.dict(), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


## Define state ------------------------------------------------------------------------
# This defines the object that is passed between each node
# in the graph. We will create different nodes for each agent and tool
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history: List[BaseMessage]
    sender: str


agent_names = list(agents_metadata.keys())

for name in agent_names:
    agents_metadata[name]['node'] = create_agent(
            llm,
            agents_metadata[name]['tools'],
            system_message=agents_metadata[name]['prompt'],
        )

    agents_metadata[name]['node'] = functools.partial(agent_node, agent=agents_metadata[name]['node'], name=name)