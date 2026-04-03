from agents.prompts import wordle_chain
from core.models import WordleState, GuessResponse
from core.nyt_wordle import NYTWordleSolver

wordle = NYTWordleSolver()

_INVOKE_PAYLOAD_KEYS = [
    "attempted_words", "forbidden_locations", "word",
    "letters_in_wrong_position", "letters_not_in_word", "attempted_words_results",
]

def word_guess_node(state: WordleState):
    payload = {k: state[k] for k in _INVOKE_PAYLOAD_KEYS}

    output: GuessResponse | None = None
    for attempt in range(3):
        try:
            output = wordle_chain.invoke(payload)
            # Double-check length in case the validator was bypassed
            if len(output.word) == 5 and output.word.isalpha():
                break
            print(f"[RETRY {attempt+1}] LLM returned invalid word '{output.word}' ({len(output.word)} letters). Retrying...")
        except Exception as e:
            print(f"[RETRY {attempt+1}] Parsing error: {e}. Retrying...")
            output = None

    if output is None or len(output.word) != 5:
        fallback = "crane"  # sensible high-entropy fallback
        print(f"[FALLBACK] Using fallback word '{fallback}' after 3 failed attempts.")
        word = fallback
    else:
        word = output.word

    return {
        "attempted_words": [word],
        "remaining_attempts": 1,
        "solved": False,
    }

def guess_validate_node(state: WordleState):
    guess = state["attempted_words"][-1]
    validation = wordle.attempt(guess)

    right, wrong, absent = wordle.calculate_wordle_feedback(guess, validation)

    # 1. Update Fixed Pattern (Greens)
    current_pattern = list(state["word"])
    for i, val in enumerate(validation):
        if val == 1:
            current_pattern[i] = guess[i]
    updated_word = "".join(current_pattern)

    # 2. Update Forbidden Locations (Yellows and Grays)
    # We create a fresh dict from the old state to modify it
    new_forbidden = dict(state.get("forbidden_locations", {}))
    for i, val in enumerate(validation):
        if val == 2 or val == 0:  # Yellow or Gray
            letter = guess[i]
            if letter not in new_forbidden:
                new_forbidden[letter] = []
            if i not in new_forbidden[letter]:
                new_forbidden[letter].append(i)

    # 3. Sanitize Banned Letters
    known_letters = set([c for c in updated_word if c != "_"]) | set(state["letters_in_wrong_position"]) | set(wrong)
    truly_absent = [l for l in absent if l not in known_letters]

    return {
        "word": updated_word,
        "letters_in_wrong_position": list(set(wrong)),
        "letters_not_in_word": list(set(truly_absent)),
        "forbidden_locations": new_forbidden,  # Replaces the dict in state
        "attempted_words_results": [validation],
        "solved": validation == [1, 1, 1, 1, 1],
        "solution_grid": state["solution_grid"] + wordle.get_grid(validation),
    }