from langchain.tools import tool

from src.core.nyt_wordle import NYTWordleSolver

wordle = NYTWordleSolver()

@tool
def attempt_wordle_guess(guess):
    return wordle.attempt(guess)
