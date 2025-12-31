import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama


mcp_client = MultiServerMCPClient(
    {
        "result_publisher": {
            "transport": "http",
            "url": "http://localhost:8010/mcp",
        }
    }
)

async def test():
    result_publisher = ChatOllama(
        model="gpt-oss:latest",
        temperature=0.8,
    )

    tools = await mcp_client.get_tools()

    print(tools)

    result_publisher = result_publisher.bind_tools(tools)

    print(result_publisher.invoke("publish 'hi' in slack."))

asyncio.run(test())
