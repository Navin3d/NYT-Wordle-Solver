from src.agents.prompts import wordle_chain
from src.core.models import WordleState, GuessResponse
from src.core.nyt_wordle import NYTWordleSolver

wordle = NYTWordleSolver()

def word_guess_node(state: WordleState):
    output: GuessResponse = wordle_chain.invoke({
        "attempted_words": state["attempted_words"],
        "forbidden_locations": state["forbidden_locations"],
        "word": state["word"],
        "letters_in_wrong_position": state["letters_in_wrong_position"],
        "letters_not_in_word": state["letters_not_in_word"],
        "attempted_words_results": state["attempted_words_results"],
    })
    return {
        "attempted_words": [output.word],
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