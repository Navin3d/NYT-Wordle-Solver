from agents.prompts import wordle_chain
from core.game import NYTWordleSolver
from core.models import GuessResponse, WordleState

GUESS_NODE = "GUESS"
VALIDATE_NODE = "VALIDATE"
_INVOKE_PAYLOAD_KEYS = [
    "attempted_words",
    "forbidden_locations",
    "word",
    "letters_in_wrong_position",
    "letters_not_in_word",
    "attempted_words_results",
]

wordle = NYTWordleSolver()

def word_guess_node(state: WordleState):
    # payload = {key: state[key] for key in _INVOKE_PAYLOAD_KEYS}
    output: GuessResponse | None = None
    past_solutions = []

    for attempt in range(180):
        # print("Attempted words: ", state["attempted_words"])
        # print("Past solutions: ", state["past_solutions"])
        try:
            output = wordle_chain.invoke(dict(state))
            if output is not None and len(output.word) == 5 and output.word.isalpha():
                if wordle.is_word_in_previous_answers(output.word):
                    state["past_solutions"].append(output.word)
                    print(
                        f"[RETRY {attempt+1}] LLM returned word '{output.word}' "
                        f"which was already published by NYT. Retrying..."
                    )
                    past_solutions.append(output.word)
                    continue
                break
            if output is not None:
                print(
                    f"[RETRY {attempt+1}] LLM returned invalid word '{output.word}' "
                    f"({len(output.word)} letters). Retrying..."
                )
        except Exception as error:
            print(f"[RETRY {attempt+1}] Parsing error: {error}. Retrying...")
            output = None

    if output is None or len(output.word) != 5:
        fallback = "crane"
        print(f"[FALLBACK] Using fallback word '{fallback}' after 3 failed attempts.")
        word = fallback
    else:
        word = output.word

    return {
        "attempted_words": [word],
        # "remaining_attempts": state["remaining_attempts"],
        # "past_solutions": past_solutions,
        "solved": False,
    }

def validate_guess_node(state: WordleState):
    guess = state["attempted_words"][-1]
    validation = wordle.attempt(guess)

    _, wrong, absent = wordle.calculate_wordle_feedback(guess, validation)

    current_pattern = list(state["word"])
    for index, value in enumerate(validation):
        if value == 1:
            current_pattern[index] = guess[index]
    updated_word = "".join(current_pattern)

    new_forbidden = {**state.get("forbidden_locations", {})}
    for index, value in enumerate(validation):
        if value in {0, 2}:
            letter = guess[index]
            new_forbidden.setdefault(letter, [])
            if index not in new_forbidden[letter]:
                new_forbidden[letter].append(index)

    updated_wrong_position = list(set(state["letters_in_wrong_position"] + wrong))
    known_letters = set(updated_word.replace("_", "")) | set(updated_wrong_position)
    truly_absent = [letter for letter in absent if letter not in known_letters]

    return {
        "word": updated_word,
        "letters_in_wrong_position": updated_wrong_position,
        "letters_not_in_word": list(set(state["letters_not_in_word"] + truly_absent)),
        "forbidden_locations": new_forbidden,
        # "attempted_words": state["attempted_words"],
        "attempted_words_results": state["attempted_words_results"] + [validation],
        "remaining_attempts": max(state["remaining_attempts"] - 1, 0),
        "solved": validation == [1, 1, 1, 1, 1],
        "solution_grid": state["solution_grid"] + wordle.get_grid(validation),
    }
