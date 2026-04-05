import asyncio
from typing import Any, cast

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from agents.prompts import llm, result_publish_prompt
from core.models import WordleState

PUBLISH_NODE = "PUBLISH"

_mcp_client = MultiServerMCPClient(
    cast(Any, {
        "result_publisher": {
            "transport": "http",
            "url": "http://localhost:8010/mcp",
        }
    })
)

tools = asyncio.run(_mcp_client.get_tools())


async def result_publish_node(state: WordleState):
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=result_publish_prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    await agent_executor.ainvoke(dict(state))
    return {}

