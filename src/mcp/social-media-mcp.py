import slack
from fastmcp import FastMCP

mcp = FastMCP("Social media MCP Server")

@mcp.tool
def send_message_to_slack(message: str):
    slack.send_message_to_slack(message)
    print("Sent message to Slack!")

@mcp.tool
def post_comment_in_nyt(comment: str):
    print("Posting comment in NYT!")

if __name__ == "__main__":
    mcp.run(transport="http", port=8010)
