from typing import TypedDict, Annotated

from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import StateGraph

# from src.agents.tools import attempt_wordle_guess


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
# _llm = _llm.bind_tools([attempt_wordle_guess()])


def word_guess_node(state: WordleState) -> WordleState:
    return state

def guess_validate_node(state: WordleState) -> WordleState:
    return state

def result_publish_node(state: WordleState) -> WordleState:
    return state


NODE_NAMES = {
    "guess": "GUESS",
    "validate": "VALIDATE",
    "result_publish": "PUBLISH",
}

graph_builder = StateGraph(state_schema=WordleState)
graph_builder.add_node(NODE_NAMES["guess"], word_guess_node)
graph_builder.add_node(NODE_NAMES["validate"], guess_validate_node)
graph_builder.add_node(NODE_NAMES["result_publish"], result_publish_node)

graph_builder.add_conditional_edges(NODE_NAMES["guess"], guess_validate_node, path_map={
    # NODE_NAMES["guess"]:NODE_NAMES["validate"],
    # NODE_NAMES["validate"]:NODE_NAMES["guess"],
    # NODE_NAMES["validate"]:NODE_NAMES["result_publish"],
})

graph_builder.add_edge(START, NODE_NAMES["guess"])
graph_builder.add_edge(NODE_NAMES["guess"], NODE_NAMES["validate"])
graph_builder.add_edge(NODE_NAMES["validate"], NODE_NAMES["guess"])
graph_builder.add_edge(NODE_NAMES["validate"], NODE_NAMES["result_publish"])
graph_builder.add_edge(NODE_NAMES["result_publish"], END)

memory = InMemorySaver()
graph = graph_builder.compile(memory)

print(graph.get_graph().draw_mermaid())
