from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agents.publisher import PUBLISH_NODE, result_publish_node
from agents.solver import GUESS_NODE, VALIDATE_NODE, word_guess_node, validate_guess_node
from core.models import WordleState


def build_wordle_graph() -> StateGraph:
    graph_builder = StateGraph(state_schema=WordleState)
    graph_builder.add_node(GUESS_NODE, word_guess_node)
    graph_builder.add_node(VALIDATE_NODE, validate_guess_node)
    graph_builder.add_node(PUBLISH_NODE, result_publish_node)

    graph_builder.add_conditional_edges(
        VALIDATE_NODE,
        _decide_next_node,
        {
            PUBLISH_NODE: PUBLISH_NODE,
            GUESS_NODE: GUESS_NODE,
        },
    )

    graph_builder.add_edge(START, GUESS_NODE)
    graph_builder.add_edge(GUESS_NODE, VALIDATE_NODE)
    graph_builder.add_edge(PUBLISH_NODE, END)

    return graph_builder


def _decide_next_node(state: WordleState) -> str:
    if state["solved"] is True or state["remaining_attempts"] <= 0:
        return PUBLISH_NODE
    return GUESS_NODE
