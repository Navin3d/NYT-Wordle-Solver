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
            You are a Wordle Solver operating in STRICTOR HARD MODE.
            
            strictly 5 letter word.
            
            ### CRITICAL CONSTRAINT: WORD LENGTH
            - The "word" field MUST be EXACTLY 5 letters long and lowercase.
            - Even if you only know 1 letter, you MUST provide a full 5-letter word (e.g., if you know 'e' is at the end, guess 'CRANE', not 'CRAN').
            - DO NOT return underscores. Return a complete, valid English word.
            
            ### 🚫 POSITION EXCLUSION (STRICT HARD MODE)
            The following letters are known to be in the word, but are FORBIDDEN at these specific indices (0-4):
            {forbidden_locations}
            
            Mandatory: If you see 's': [0, 3], your guess MUST NOT have 's' at the 1st or 4th character.
    
            ### RULES OF CONFORMITY:
            1. WORD PATTERN: Your guess MUST have these letters in these exact spots: {word}
            2. REQUIRED LETTERS: Your guess MUST contain all of these: {letters_in_wrong_position}.
            3. BANNED LETTERS: Your guess MUST NOT contain any of: {letters_not_in_word}.
            4. POSITION LOCK: If a letter was '2' (Yellow) at a specific index, you CANNOT put that letter in that same index again.
            
            ### DATA INTEGRITY CHECK:
            - If a letter is in {word} or {letters_in_wrong_position}, ignore it if it also appears in {letters_not_in_word} (this handles the Wordle "duplicate letter" rule).
            - If multiple solutions exist, pick the one that uses common consonants (R, S, T, L, N) to narrow the field.
            
            ### REASONING STEPS (Internal):
            Step 1: Identify possible words matching the 5 letter pattern {word}.
            Step 2: Filter out any words containing letters from the Banned List.
            Step 3: Ensure all letters from the Required List are present.
            Step 4: Verify Hard Mode: Ensure no Required Letter is placed in a position where it previously turned Yellow.
            
            ### OUTPUT:
            Return ONLY the JSON format specified.
            Parse the output in this format: {output_format}
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
'''














'''
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
            attempted_words_results: {attempted_words_results} results will be in list[list[int]]
            word: {word}
            letters_in_wrong_position: {letters_in_wrong_position}
            letters_not_in_word: {letters_not_in_word}
            
            word: eg) "s__l_"
            → Position 0 must be 's'
            → Position 3 must be 'l'  
            → Positions 1,2,4 are open (but respect letters_not_in_word)
            
            Next guess must match: s[not excluded][not excluded]l[not excluded]
            
            ### STRATEGY PRIORITIES (Optimal Play):
            1. **Strictly obey Hard Mode constraints** — every guess must be compatible with all prior feedback.
            2. **Maximize information gain**: Choose guesses that split the remaining possible solutions into the most balanced groups (highest expected entropy reduction). This is the mathematically optimal approach.
            3. If no guesses remain, or to compute candidates efficiently:
               - Mentally maintain/filter the list of remaining possible answers (original NYT solution list ~2,309-2,315 words, minus used answers).
               - Prefer guesses that are themselves possible answers when tie-breaking (to allow potential early wins).
            5. Prioritize words that test multiple uncertain letters/positions while respecting constraints.
            6. Avoid repeating failed patterns or low-information guesses.
            
            For each response:
            - List the known constraints (1 fixed, must-include 2, banned 0).
            - If only 1 possibility remains → guess it to win.
            - If [1,1,1,1,1] achieved → celebrate the win.
            
            REASON step-by-step using above state, then output GuessResponse.
            
            Parse the output in this format: {output_format}
            All fields in output are required not null.
'''
