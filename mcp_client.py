import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_mcp_adapters.tools import load_mcp_tools

# MCP server launch config
server_params = StdioServerParameters(
    command = "python"
    args = ["weather_server.py"]
)

# LangGraph State definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]

async def create_graph(session):

    # Load tools from MCP server
    tools = await load_mcp_tools(session)

    # LLM Configuration
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0, google_api_key = "xxx")
    llm_with_tools = llm.bind_tools (tools)


    # Prompt template with user/assistant chat only
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to get the current weather for a location."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools


    # Define chat node
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Build LangGraph with tool routing
    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add.conditional_edges("chat_node", tools_condition, {
        "tools": "tools_node",
        "__end__": END
    })
    graph.add_edge("tool_node", "chat_node")

    return graph.compile(checkpointer = MemorySaver())