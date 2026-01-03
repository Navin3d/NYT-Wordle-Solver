import os

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain_ollama import ChatOllama

from src.core.models import GuessResponse

_wordle_output_parser = PydanticOutputParser(pydantic_object=GuessResponse)

_wordle_guessing_prompt = ChatPromptTemplate.from_messages([
    # - Call the 'attempt_wordle_guess' tool with exactly 5-letter words
    (
        "system",
        """
            You are an expert Wordle solver playing in **Hard Mode** for the New York Times Wordle game. Your goal is to solve the puzzle in as few guesses as possible (ideally ≤4 on average, never more than 6), using optimal information-theoretic strategy while strictly adhering to all revealed hints.

            ### WORDLE RULES (NYT VERSION):
            - 5-letter words lower case letter only.
            - 5 guesses maximum.
            - Feedback: 🟩 (1 = correct letter, correct position), 🟨 (2 = correct letter, wrong position), ⬜ (0 = letter not in word).
            - **Hard Mode rules are enforced**: Every guess MUST incorporate all previous hints:
                - 0 = White (letters must stay in their exact positions)
                - 1 = Green (letter in solution, CORRECT position) 
                - 2 = Yellow (letters must be used in new positions (not in any previously 2/0 positions for that letter)
            - Guesses must be valid 5-letter English words (from the NYT's allowed guess list).
            
            CURRENT STATE:
            attempted_words: {attempted_words}
            attempted_words_results: {attempted_words_results}
            letters_in_right_position: {letters_in_right_position}
            letters_in_wrong_position: {letters_in_wrong_position}
            letters_not_in_word: {letters_not_in_word}
            
            ### STRATEGY PRIORITIES (Optimal Play):
            1. **Strictly obey Hard Mode constraints** — every guess must be compatible with all prior feedback.
            2. **Maximize information gain**: Choose guesses that split the remaining possible solutions into the most balanced groups (highest expected entropy reduction). This is the mathematically optimal approach.
            3. If no guesses remain, or to compute candidates efficiently:
               - Mentally maintain/filter the list of remaining possible answers (original NYT solution list ~2,309-2,315 words, minus used answers).
               - Prefer guesses that are themselves possible answers when tie-breaking (to allow potential early wins).
            4. Early game (first 1-2 guesses): Use high-entropy openers like 'audio'.
            5. Mid/late game: Prioritize words that test multiple uncertain letters/positions while respecting constraints.
            6. Avoid repeating failed patterns or low-information guesses.
            
            ### STEP-BY-STEP REASONING REQUIRED:
            For each response:
            - List the known constraints (1 fixed, must-include 2, banned 0).
            - Estimate remaining possible words (if few, list them; if many, note approximate count).
            - Explain why your chosen guess maximizes information (e.g., tests key vowels/consonants, eliminates large branches).
            - If only 1 possibility remains → guess it to win.
            - If [1,1,1,1,1] achieved → celebrate the win.
            
            REASON step-by-step using above state, then output GuessResponse.
            
            Parse the output in this format: {output_format}
            All fields in output are required not null.    
        """
    )
]).partial(output_format=_wordle_output_parser.get_format_instructions())

result_publish_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        '''You are a Wordle result publishing agent. Publish results using MCP tools: Slack + NYT.

        **INPUT STATE:**
        attempted_words: {attempted_words}
        letters_in_right_position: {letters_in_right_position}
        letters_in_wrong_position: {letters_in_wrong_position}
        letters_not_in_word: {letters_not_in_word}
        attempts_left: {attempts_left}
        solved: {solved}
        
        **WORKFLOW:**
        1. Generate Wordle share grid from state (🟩=green, 🟨=yellow, ⬜=gray).
        2. Call MCP tools IN SEQUENCE: send_message_to_slack(grid_message) then post_comment_in_nyt(comment_message).
        
        **EXAMPLE MESSAGES (adapt to state):**
        Slack: """
        Wordle {{attempts_made}}/6  # Escaped {{ }}
        🟩⬜🟨⬜⬜ {first_word}
        🟩🟩⬜⬜🟨 {second_word}
        Wordle Agent Complete! { "solved": {solved}, "greens": {greens_count} }
        """

        NYT: """
        Wordle Solver: {{attempts_made}}/6 { "status": "GENIUS!" if solved else "Better luck tomorrow!", "grid": "🟩🟩🟩🟩🟩" }
        """

        **RULES:**
        - Slack: Full grid + details (use {attempted_words}, {solved}).
        - NYT: Compact comment with status/grid emoji.
        - Compute attempts_made = 6 - {attempts_left}.
        - Success: "✅ Published to Slack + NYT".
        - ALWAYS call both tools in sequence.
        '''
    ),
    MessagesPlaceholder("agent_scratchpad"),
])

llm = ChatOllama(
    model=os.environ["MODEL_NAME"],
    temperature=0.1,
)

wordle_chain = RunnableSequence(_wordle_guessing_prompt, llm, _wordle_output_parser)













'''

            You are a Wordle solver agent. Follow these rules exactly:

            WORDLE RULES:
            - Solve 5-letter words only
            - Maximum 5 attempts total
            - Tool returns array of 5 numbers: [0,1,2] format
            
            FEEDBACK CODES:
            - 0 = White (letter NOT in solution at all)
            - 1 = Green (letter in solution, CORRECT position) 
            - 2 = Yellow (letter in solution, WRONG position)
            
            CURRENT STATE:
            attempted_words: {attempted_words}
            letters_in_right_position: {letters_in_right_position}
            letters_in_wrong_position: {letters_in_wrong_position}
            letters_not_in_word: {letters_not_in_word}
            
            STRATEGY:
            1. First guess: Use common letters ("crane", "slate", "audio") if no attempts made
            2. Respect current state:
               - NEVER use letters from letters_not_in_word (all positions)
               - ALWAYS place letters from letters_in_right_position in their exact positions
               - Use letters from letters_in_wrong_position in new positions (avoid original positions)
            3. Prioritize filling known green positions first
            4. Eliminate positions ruled out by yellow feedback from prior attempts
            5. Choose words maximizing information gain from remaining possible letters
            6. Track letter frequencies and positions from all feedback
            
            WIN CONDITION: Get all 5 greens [1, 1, 1, 1, 1]
            After each attempt, explain your reasoning and meaning for the guss word clearly using the current state before next guess.
            
            Parse the output in this format: {output_format}
            All fields in output are required not null.
            
            Current attempts remaining: {remaining_attempts}
        
'''