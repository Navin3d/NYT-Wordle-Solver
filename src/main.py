import uuid, asyncio

from dotenv import load_dotenv
load_dotenv(verbose=True)

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from src.agents.result_publisher import result_publish_node, NODE_NAMES
from src.agents.wordle_solver import word_guess_node, guess_validate_node
from src.core.models import WordleState


def condition_edge(state: WordleState) -> str:
    return NODE_NAMES["result_publish"] if state["solved"] is True or int(state["remaining_attempts"]) > 4 else NODE_NAMES["guess"]

graph_builder = StateGraph(state_schema=WordleState)
graph_builder.add_node(NODE_NAMES["guess"], word_guess_node)
graph_builder.add_node(NODE_NAMES["validate"], guess_validate_node)
graph_builder.add_node(NODE_NAMES["result_publish"], result_publish_node)

graph_builder.add_conditional_edges(NODE_NAMES["validate"], condition_edge, {
    NODE_NAMES["result_publish"]: NODE_NAMES["result_publish"],  # Map bool/cond to str
    NODE_NAMES["guess"]: NODE_NAMES["guess"]
})

graph_builder.add_edge(START, NODE_NAMES["guess"])
graph_builder.add_edge(NODE_NAMES["guess"], NODE_NAMES["validate"])
graph_builder.add_edge(NODE_NAMES["result_publish"], END)

memory = InMemorySaver()
graph = graph_builder.compile(memory)

print(graph.get_graph().draw_mermaid())


inputs = {
    "attempted_words": [],
    "attempted_words_results": [],
    "letters_in_right_position": [],
    "letters_in_wrong_position": [],
    "letters_not_in_word": [],
    "solved": False,
    "solution_grid": "",
    "remaining_attempts": 0,
}

config = {
    "configurable": {
        "thread_id": uuid.uuid4()
    }
}

async def run_graph():
    async for event in graph.astream(inputs, config, stream_mode="values"):
        messages = event.get("context", [])
        if messages:
            print(messages)
            last_msg = messages[-1]
            print(f"AI: {last_msg.content}")

asyncio.run(run_graph())
