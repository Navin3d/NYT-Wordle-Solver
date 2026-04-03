import asyncio

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_tool_calling_agent

from agents.prompts import llm, result_publish_prompt
from core.models import WordleState

_mcp_client = MultiServerMCPClient(
    {
        "result_publisher": {
            "transport": "http",
            "url": "http://localhost:8010/mcp",
        }
    }
)

NODE_NAMES = {
    "guess": "GUESS",
    "validate": "VALIDATE",
    "result_publish": "PUBLISH",
}
tools = asyncio.run(_mcp_client.get_tools())

async def result_publish_node(state: WordleState):
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=ChatPromptTemplate.from_messages([
        (
            "system",
            '''
                You are an helpful ai agent

                Call MCP tools as said:
                   - `send_message_to_slack(message)`
                   - `post_comment_in_nyt(message)`
            '''
        ),
        ("human", "just send whatever i give u it consists of colors input: {input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]))
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    await agent_executor.ainvoke({ "input": state["solution_grid"] })
    return {}







async def trial():
    tools = await _mcp_client.get_tools()
    print(tools)
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            '''
                You are an helpful ai agent
                
                Call MCP tools as said:
                   - `send_message_to_slack(grid_message)`
                   - `post_comment_in_nyt(comment_message)`
            '''
        ),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    result = await agent_executor.ainvoke({ "input": "publish 'hi' in slack."})
    print(result)


if __name__ == "__main__":
    asyncio.run(trial())
