import uuid, asyncio

from dotenv import load_dotenv
load_dotenv(verbose=True)

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from rich.console import Console
from rich.panel import Panel

from agents.result_publisher import result_publish_node, NODE_NAMES
from agents.wordle_solver import word_guess_node, guess_validate_node
from core.models import WordleState


def condition_edge(state: WordleState) -> str:
    return NODE_NAMES["result_publish"] if state["solved"] is True or int(state["remaining_attempts"]) > 5 else NODE_NAMES["guess"]

def main():
    graph_builder = StateGraph(state_schema=WordleState)
    graph_builder.add_node(NODE_NAMES["guess"], word_guess_node)
    graph_builder.add_node(NODE_NAMES["validate"], guess_validate_node)
    graph_builder.add_node(NODE_NAMES["result_publish"], result_publish_node)

    graph_builder.add_conditional_edges(NODE_NAMES["validate"], condition_edge, {
        NODE_NAMES["result_publish"]: NODE_NAMES["result_publish"],
        NODE_NAMES["guess"]: NODE_NAMES["guess"]
    })

    graph_builder.add_edge(START, NODE_NAMES["guess"])
    graph_builder.add_edge(NODE_NAMES["guess"], NODE_NAMES["validate"])
    graph_builder.add_edge(NODE_NAMES["result_publish"], END)

    memory = InMemorySaver()
    graph = graph_builder.compile(memory)

    print(graph.get_graph().draw_mermaid())

    inputs = {
        "word": "_____",
        "forbidden_locations": {},
        "attempted_words": [],
        "attempted_words_results": [],
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

    console = Console()

    async def run_graph():
        with console.status("[bold green]Agent is solving Wordle...") as status:
            final_state = None
            async for event in graph.astream(inputs, config, stream_mode="values"):
                final_state = event
                # Print a neat small update for each step
                if event.get("word") and event["word"] != "_____":
                    console.print(f"[bold blue]Step:[/bold blue] Guessing [yellow]{event['word']}[/yellow]... (Attempts: {event['remaining_attempts']})")
            
            console.print("\n")
            console.print(Panel(
                final_state["solution_grid"], 
                title="[bold green]Final Wordle Result[/bold green]", 
                expand=False
            ))

    asyncio.run(run_graph())


if __name__ == "__main__":
    main()
