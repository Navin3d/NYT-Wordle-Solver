from langchain.tools import tool

from core.nyt_wordle import NYTWordleSolver

wordle = NYTWordleSolver()

@tool
def attempt_wordle_guess(guess):
    return wordle.attempt(guess)
