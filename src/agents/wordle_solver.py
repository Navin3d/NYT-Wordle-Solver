from src.agents.prompts import wordle_chain
from src.core.models import WordleState, GuessResponse
from src.core.nyt_wordle import NYTWordleSolver

wordle = NYTWordleSolver()

def word_guess_node(state: WordleState):
    output: GuessResponse = wordle_chain.invoke({
        "attempted_words": state["attempted_words"],
        "letters_in_right_position": state["letters_in_right_position"],
        "letters_in_wrong_position": state["letters_in_wrong_position"],
        "letters_not_in_word": state["letters_not_in_word"],
        "attempted_words_results": state["attempted_words_results"],
        # "len_letters_in_right_position": len(state["letters_in_right_position"]),
    })
    return {
        "attempted_words": [output.word],
        "remaining_attempts": 1,
        "solved": False,
    }
def guess_validate_node(state: WordleState):
    guess = state["attempted_words"][-1]
    print("Guess '{}'".format(state["attempted_words"]))
    validation = wordle.attempt(guess)
    right_pos, wrong_pos, not_in_word = wordle.calculate_wordle_feedback(guess, validation)

    grid = state["solution_grid"] + wordle.get_grid(validation)
    return {
        "letters_in_right_position": right_pos,
        "letters_in_wrong_position": wrong_pos,
        "letters_not_in_word": not_in_word,
        "attempted_words_results": [validation],
        "solved": True if validation == [1, 1, 1, 1, 1] else False,
        "solution_grid": grid,
    }
