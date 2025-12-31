from langchain_ollama import ChatOllama
from langgraph.graph.message import MessagesState
from langgraph.graph.state import StateGraph


class StateMessages(MessagesState):


_llm = ChatOllama(
    model="deepseek-r1:8b",
    temperature=0.8,
)

graph = StateGraph()
