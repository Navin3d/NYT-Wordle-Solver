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
            You are a Wordle solver agent. Follow these rules exactly:

            **CURRENT STATE:**
            - attempted_words: {attempted_words}  # Past guesses
            - letters_in_right_position: {letters_in_right_position}  # SHOULD KEEP IN FIXED POSITION AS BEFORE
            - letters_in_wrong_position: {letters_in_wrong_position}  # Must use somewhere, NOT original position of previous guess
            - letters_not_in_word: {letters_not_in_word}  # NEVER use these letters
            - last_guess: {last_guess}
            
            **CRITICAL RULES (VIOLATE = FAIL):**
            1. GREEN POSITIONS: Build word with EXACT letters in EXACT positions.
               - letters_in_right_position=["E"] → word[4] MUST = "E" (0-indexed last pos)
               - Multiple: ["S", "E"] → word[0]="S", word[4]="E"
            2. AVOID letters_not_in_word everywhere.
            3. PLACE letters_in_wrong_position in NEW positions only.
            4. NEVER repeat failed position patterns from attempted_words.
            
            **EXAMPLE REASONING:**
            STATE: attempted_words=["crane"], letters_in_right_position=[], letters_in_wrong_position=["c","r","a","n","e"], letters_not_in_word=[]
            → Guess "slate" (rearranges common letters)
            
            STATE: attempted_words=["crane", "slate"], letters_in_right_position=["e"], letters_in_wrong_position=["s","l","a","t"], letters_not_in_word=["c","r","n"]
            → Guess "stare" (e in pos5, rearrange s/l/a/t + new vowel)
            
            **VISUALIZE HISTORY:**
            Reconstruct feedback grids mentally:
            crane → ⬜🟨⬜🟨🟩 (e green pos5 → future: _ _ _ _ E)
            slate → 🟨⬜🟨⬜🟩
            
            **NEXT GUESS:**
            - 5 letters, valid English word
            - Lock greens: position {letters_in_right_position} fixed
            - Maximize info: common letters first
            
            After each attempt, explain your reasoning and meaning for the guss word clearly using the current state before next guess.
            
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
    temperature=0.7,
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