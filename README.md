# 🧩 NYT Wordle AI Solver

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflows-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Package Manager: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A cutting-edge AI agent powered by **LangGraph** designed to solve the daily New York Times Wordle puzzle with human-like reasoning and strategic guessing.

---

## ✨ Features

-   **🧠 Graph-Based Intelligence**: Orchestrates guesses and validations using a cyclic directed graph via **LangGraph**.
-   **🛠️ MCP Integration**: Built-in support for Model Context Protocol (MCP) to interact with external tools.
-   **💬 Slack Integration**: Automatically publishes the day's solution grid to your Slack channels.
-   **🎨 Rich Terminal UI**: Features a beautiful console experience with real-time spinners, colored logs, and progress tracking.
-   **⚡ Powered by uv**: Ultra-fast dependency management and execution.

---

## 🏗️ Architecture

The solver operates as a state machine with three primary nodes:

```mermaid
graph TD;
        __start__([<p>__start__</p>]):::first
        GUESS(GUESS)
        VALIDATE(VALIDATE)
        PUBLISH(PUBLISH)
        __end__([<p>__end__</p>]):::last
        GUESS --> VALIDATE;
        VALIDATE -.-> GUESS;
        VALIDATE -.-> PUBLISH;
        __start__ --> GUESS;
        PUBLISH --> __end__;
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
```

---

## 🚀 Getting Started

### Prerequisites

-   [uv](https://github.com/astral-sh/uv) installed on your system.
-   An OpenAI API Key or a local [Ollama](https://ollama.com/) instance.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Navin3d/NYT-Wordle-Solver.git
    cd NYT-Wordle-Solver
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure environment:**
    Create a `.env` file in the `src` directory:
    ```env
    SLACK_BOT_TOKEN=xoxb-111111-22221222-jhghg
	SLACK_CHANNEL_ID=#general
	MODEL_NAME=gemma4:latest
    ```

---

## 🎮 Usage

Run the solver directly from the project root:

```bash
uv run python src/main.py
```

---

## 🛠️ Tech Stack

-   **Logic**: [LangGraph](https://github.com/langchain-ai/langgraph) / [LangChain](https://github.com/langchain-ai/langchain)
-   **Language**: Python 3.13
-   **UI**: [Rich](https://github.com/Textualize/rich)
-   **Package Manager**: [uv](https://github.com/astral-sh/uv)
-   **MCP**: [FastMCP](https://github.com/jlowin/fastmcp)

## References
- [Wordle Solver](https://www.nytimes.com/svc/wordle/v2/2026-01-01.json)
- [Fast MCP](https://gofastmcp.com/getting-started/quickstart)
- [Mermaid to PIC](https://www.mermaidflow.app/editor)
- [Excali Draw](https://excalidraw.com/)
