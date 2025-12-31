import os

from slack_sdk import WebClient
from dotenv import load_dotenv
from slack_sdk.errors import SlackApiError

load_dotenv(verbose=True)

slack_token = os.environ["SLACK_BOT_TOKEN"]
channel_id = os.environ["SLACK_CHANNEL_ID"]

client = WebClient(token=slack_token)

def send_message_to_slack(message, channel=channel_id):
    try:
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        assert e.response["error"]
