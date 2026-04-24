import json

from langchain.tools import tool
from core.game import NYTWordleSolver


wordle = NYTWordleSolver()

@tool
def attempt_wordle_guess(guess: str) -> list[int]:
    """
    Attempts a guess at the Wordle puzzle.

    Args:
        guess: The word to guess.

    Returns:
        A list of integers representing the feedback for the guess.
        1 = Correct position
        2 = Wrong position
        0 = Not in word
    """
    return wordle.attempt(guess)

@tool
def is_word_in_previous_answers(guessword: str) -> bool:
    """
    Checks if a word has been used as a previous answer in Wordle.

    Args:
        guessword: The word to check.

    Returns:
        True if the word has been used as a previous answer, False otherwise.
    """
    return guessword.upper() in wordle.get_previous_solutions()
