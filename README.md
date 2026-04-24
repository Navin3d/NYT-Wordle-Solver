# 🧩 NYT Wordle AI Solver

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_Workflows-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Package Manager: uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

A LangGraph-powered AI agent built to solve the daily New York Times Wordle puzzle using a structured workflow and MCP-enabled publishing.

---

## ✨ Features

-   **🧠 Graph-Based Intelligence**: Uses a LangGraph workflow to manage guessing, validation, and publishing.
-   **🛠️ MCP Integration**: Publishes results through external MCP tools (Slack, WhatsApp, NYT).
-   **💬 Slack Publishing**: Sends the Wordle result grid to a configured Slack channel.
-   **📱 WhatsApp Integration**: Automated WhatsApp messaging using `pywhatkit`.
-   **📝 NYT Commenting**: Generates and posts friendly comments for the NYT community.
-   **🎨 Rich Terminal UI**: Provides live feedback and polished terminal output.
-   **🧱 Modular Codebase**: Clear separation between game logic, prompts, solver nodes, and publishing.

---

## 🚀 Project Structure

-   `src/app.py` — main application entrypoint
-   `src/core/game.py` — Wordle game rules, feedback, and grid rendering
-   `src/core/graph_builder.py` — LangGraph workflow construction and node transitions
-   `src/agents/prompts.py` — LLM prompt templates and chain configuration
-   `src/agents/solver.py` — solver node implementations for guessing and validation
-   `src/agents/publisher.py` — MCP publisher node
-   `src/mcp/social-media-mcp.py` — MCP server hosting Slack, WhatsApp, and NYT tools
-   `src/mcp/whatsapp.py` — WhatsApp messaging utility

---

## 🏗️ Architecture

The solver runs as a three-node state machine:

```mermaid
graph TD;
    __start__([__start__])
    GUESS(GUESS)
    VALIDATE(VALIDATE)
    PUBLISH(PUBLISH)
    __end__([__end__])

    __start__ --> GUESS;
    GUESS --> VALIDATE;
    VALIDATE -.-> GUESS;
    VALIDATE -.-> PUBLISH;
    PUBLISH --> __end__;
```

---

##  Getting Started

### Prerequisites

-   [uv](https://github.com/astral-sh/uv)
-   A compatible LLM backend configured via `MODEL_NAME`
-   A local or remote MCP endpoint

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/Navin3d/NYT-Wordle-Solver.git
    cd NYT-Wordle-Solver
    ```

2.  Install dependencies:
    ```bash
    uv sync
    ```

3.  Configure environment variables by creating `src/.env`:
    ```env
    SLACK_BOT_TOKEN=xoxb-111111-22221222-jhghg
    SLACK_CHANNEL_ID=#general
    WHATSAPP_CONTACTS_TO_SEND=+919442807217
    MODEL_NAME=gemma4:latest
    ```

### 🛠️ Running the MCP Server

Before running the solver, start the Social Media MCP server in a separate terminal:

```bash
uv run python src/mcp/social-media-mcp.py
```

> The current publisher module is configured to use an MCP service at `http://localhost:8010/mcp`.

---

##  Usage

Run the solver from the project root:

```bash
uv run python src/app.py
```

---

##  Tech Stack

-   **LangGraph** / **LangChain**
-   **Python 3.13**
-   **Rich**
-   **uv**
-   **FastMCP**

---

## References

-   [NYT Wordle JSON endpoint](https://www.nytimes.com/svc/wordle/v2/2026-01-01.json)
-   [Fast MCP Quickstart](https://gofastmcp.com/getting-started/quickstart)
-   [Mermaid.js](https://mermaid-js.github.io/mermaid/#/)
