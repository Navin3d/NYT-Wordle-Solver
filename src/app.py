import asyncio
import uuid

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.panel import Panel
from langgraph.checkpoint.memory import InMemorySaver

from core.game import INITIAL_WORD_PATTERN
from core.graph_builder import build_wordle_graph
from core.models import WordleState


def create_initial_state() -> WordleState:
    return {
        "word": INITIAL_WORD_PATTERN,
        "forbidden_locations": {},
        "attempted_words": [],
        "attempted_words_results": [],
        "letters_in_wrong_position": [],
        "letters_not_in_word": [],
        "solved": False,
        "solution_grid": "",
        "remaining_attempts": 6,
    }


async def run_graph(state: WordleState):
    memory = InMemorySaver()
    graph = build_wordle_graph().compile(memory)

    console = Console()
    console.print("[bold green]Wordle solver starting...[/bold green]\n")
    console.print(graph.get_graph().draw_mermaid())

    final_state = None
    config = {"configurable": {"thread_id": uuid.uuid4()}}

    with console.status("[bold green]Agent is solving Wordle...[/bold green]"):
        async for event in graph.astream(state, config, stream_mode="values"):
            final_state = event
            if event.get("word") and event["word"] != INITIAL_WORD_PATTERN:
                console.print(
                    f"[bold blue]Step:[/bold blue] Guessing [yellow]{event['word']}[/yellow]... "
                    f"(Remaining attempts: {event['remaining_attempts']})"
                )

    console.print()
    console.print(
        Panel(
            final_state["solution_grid"],
            title="[bold green]Final Wordle Result[/bold green]",
            expand=False,
        )
    )


def main():
    initial_state = create_initial_state()
    asyncio.run(run_graph(initial_state))


if __name__ == "__main__":
    main()
