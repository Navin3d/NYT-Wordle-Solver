from typing import TypedDict, Annotated

from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph

from src.agents.tools import attempt_wordle_guess


class WordleState(TypedDict):
    attempted_words: Annotated[list[str], add_messages]
    letters_in_right_position: Annotated[list[str], ""]
    letters_in_wrong_position: Annotated[list[str], ""]
    letters_not_in_word: Annotated[list[str], ""]
    remaining_attempts: Annotated[int, ""]
    solved: Annotated[bool, ""]
    solution_grid: Annotated[str, ""]

_llm = ChatOllama(
    model="llama3:70b-instruct-q2_K",
    temperature=0.8,
)
_llm = _llm.bind_tools([attempt_wordle_guess()])

graph = StateGraph(state_schema=WordleState)
