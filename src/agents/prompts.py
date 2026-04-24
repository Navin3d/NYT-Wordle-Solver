from datetime import datetime
import os

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain_ollama import ChatOllama

from core.models import GuessResponse

_wordle_output_parser = PydanticOutputParser(pydantic_object=GuessResponse)

_wordle_guessing_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are a Wordle Solver operating in STRICT HARD MODE.

            ### CRITICAL CONSTRAINT: WORD LENGTH
            - The "word" field MUST be EXACTLY 5 letters long and lowercase.
            - Do not return underscores or partial words. Return a complete 5-letter English word.
            - Think basic english words and dont make some complicated words initially. Use words that can be guessed by an average person.

            ### HARD MODE RULES
            - Use fixed letters from {word}.
            - Avoid letters from {letters_not_in_word}.
            - Include letters from {letters_in_wrong_position}.
            - **IMPORTANT: Do not place yellow letters in the same position again.
            - Respect {forbidden_locations}.
            - Do not use words that have been used as answers in past wordle past_solutions: {past_solutions}

            ### OUTPUT
            Return ONLY valid JSON using the format instructions.
        """
    )
]).partial(output_format=_wordle_output_parser.get_format_instructions())

result_publish_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            You are a Wordle result publishing agent. Publish results using MCP tools.

            INPUT STATE:
            attempted_words: {attempted_words}
            letters_in_wrong_position: {letters_in_wrong_position}
            letters_not_in_word: {letters_not_in_word}
            attempts_left: {remaining_attempts}
            solved: {solved}
            solution_grid: {solution_grid}

            WORKFLOW:
            1. Create a Slack message that includes the full Wordle grid and status.
            2. Create a NYT comment that is short and expressive.
            3. Call MCP tools in sequence: send_message_to_slack(message) then post_comment_in_nyt(message).

            On date 24-04-2026 the wordle id is 1,770 Todays date is {date} calculate the id
            Print id one new line and then just grip nothing else in the output. Do not include any other text or formatting or extra emojis

            Return message should be in format
            Example: 
                Wordle 1,770 attempt number/6

                <solution grid>

            RULES:
            - Slack should include attempt count and the emoji grid.
            - NYT should be compact and friendly.
            - Use attempts_made = 6 - {remaining_attempts}.
        """
    ),
    MessagesPlaceholder("agent_scratchpad"),
]).partial(date=datetime.now().strftime("%d-%m-%Y"))

llm = ChatOllama(
    model=os.environ["MODEL_NAME"],
    temperature=0.1,
)

wordle_chain = RunnableSequence(_wordle_guessing_prompt, llm, _wordle_output_parser)
