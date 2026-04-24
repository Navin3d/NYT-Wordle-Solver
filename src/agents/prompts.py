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
            - Prefer common, simple English words that an average person might guess. Avoid obscure or complex words initially.

            ### HARD MODE RULES (MANDATORY)
            - **Fixed Letters**: Use the exact letters from {word} in their positions (e.g., if {word} is "a___e", position 0 must be 'a', position 4 must be 'e').
            - **Forbidden Letters**: NEVER use any letters from {letters_not_in_word} in any position.
            - **Yellow Letters**: MUST include ALL letters from {letters_in_wrong_position} in the new word, but place them in DIFFERENT positions than where they were yellow before.
            - **Forbidden Positions**: Respect {forbidden_locations} - this is a dictionary where each key is a letter, and the value is a list of positions (0-4) where that letter CANNOT be placed again. For example, if {forbidden_locations} is {{'r': [0, 4]}}, 'r' cannot be at position 0 or 4.
            - **Past Solutions**: Do not use words that have been used as answers in past Wordle games: {past_solutions}.

            ### REASONING PROCESS
            1. Start with the fixed letters from {word}.
            2. Fill in positions with yellow letters ({letters_in_wrong_position}), ensuring they are NOT in their forbidden positions.
            3. Fill remaining positions with new letters, avoiding {letters_not_in_word} and respecting all forbidden positions.
            4. Ensure the word is valid English and fits all constraints.

            ### OUTPUT
            Return ONLY valid JSON using the format instructions. Do not include explanations outside the JSON.
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
            1. Calculate the Wordle ID: On date 24-04-2026, the Wordle ID is 1,770. For today's date ({date}), calculate the ID by adding the number of days since 24-04-2026.
            2. Calculate attempts_made = 6 - {remaining_attempts}.
            3. Create a Slack message in the format: "Wordle [ID] [attempts_made]/6\n\n{solution_grid}"
            4. Create a NYT comment that is short, expressive, and friendly (e.g., "Solved it in [attempts_made] tries!").
            5. Call MCP tools in sequence: send_message_to_slack(message), send_whatsapp_message(message, contacts={contacts}), then post_comment_in_nyt(message).

            OUTPUT FORMAT:
            - Slack message: Wordle [ID] [attempts_made]/6\n\n[solution_grid]
            - NYT comment: Short and friendly text.
            - Do not include extra text, emojis, or formatting beyond the messages.
        """
    ),
    MessagesPlaceholder("agent_scratchpad"),
]).partial(
    date=datetime.now().strftime("%d-%m-%Y"),
    contacts=os.environ["WHATSAPP_CONTACTS_TO_SEND"]
)

llm = ChatOllama(
    model=os.environ["MODEL_NAME"],
    temperature=0.1,
)

wordle_chain = RunnableSequence(_wordle_guessing_prompt, llm, _wordle_output_parser)
