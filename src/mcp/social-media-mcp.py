import slack
import whatsapp
from fastmcp import FastMCP

mcp = FastMCP("Social media MCP Server")

@mcp.tool(
    name_or_fn="send_message_to_slack",
    description="Sends a message to a default Slack channel for notifications and alerts."
)
def send_message_to_slack(message: str):
    """
        Sends a message to a default Slack channel for notifications and alerts.

        This tool posts AI-generated updates, results, or alerts to a predefined
        Slack channel. Perfect for logging agent actions, sharing computation
        results, or team notifications without needing channel configuration.

        Args:
            message: The text content to send (up to 40,000 characters).

        Returns:
            Success confirmation with timestamp, or detailed error message.

        Raises:
            SlackApiError: Authentication, rate limits, or API failures.

        Example:
            send_message_to_slack("AI agent completed analysis: 95% success rate")
    """
    slack.send_message_to_slack(message)
    print("Sent message to Slack!")

@mcp.tool(
    name_or_fn="send_whatsapp_message",
    description="Sends a WhatsApp message to a list of contacts defined in the environment."
)
def send_whatsapp_message(message: str, contacts: str = "+919442807217"):
    """
    Sends a WhatsApp message to contacts, Pass messgae and list of numbers as input.
    
    Args:
        message: The message content to send.
    """    
    contact_list = [c.strip() for c in contacts.split(",") if c.strip()]
    whatsapp.send_whatsapp_message(message, contact_list)
    return f"WhatsApp message sent to {len(contact_list)} contacts!"

@mcp.tool
def post_comment_in_nyt(comment: str):
    print("Posting comment in NYT!")

if __name__ == "__main__":
    print("Starting social media MCP server...")
    mcp.run(transport="http", port=8010)
