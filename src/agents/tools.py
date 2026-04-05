from langchain.tools import tool

from core.game import NYTWordleSolver

wordle = NYTWordleSolver()

@tool
def attempt_wordle_guess(guess):
    return wordle.attempt(guess)
