import datetime
import requests
import json

INITIAL_WORD_PATTERN = "_____"


class NYTWordleSolver:
    def __init__(self):
        self.green = chr(0x1F7E9)
        self.yellow = chr(0x1F7E8)
        self.white = chr(0x2B1C)
        self.solution = self._get_solution()
        self.previous_solutions = self._init_previous_solutions()

    def _init_previous_solutions(self) -> list[str]:
        with open("scrapping/wordle_answers.json", "r") as f:
            return json.load(f)

    def get_previous_solutions(self) -> list[str]:
        return self.previous_solutions

    def is_word_in_previous_answers(self, guessword: str) -> bool:
        """
        Checks if a word has been used as a previous answer in Wordle.

        Args:
            guessword: The word to check.

        Returns:
            True if the word has been used as a previous answer, False otherwise.
        """
        return guessword.upper() in self.get_previous_solutions()

    def _get_solution(self) -> str:
        date = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
        response = requests.get(url).json()
        return response["solution"]

    def get_grid(self, feedback: list[int]) -> str:
        mapping = {1: self.green, 2: self.yellow, 0: self.white}
        return "".join(mapping.get(value, self.white) for value in feedback) + "\n"

    def attempt(self, guess: str) -> list[int]:
        result = [0] * 5
        solution_chars: list[str | None] = list(self.solution)
        guess_chars: list[str | None] = list(guess)

        for index in range(5):
            if guess_chars[index] == solution_chars[index]:
                result[index] = 1
                solution_chars[index] = None
                guess_chars[index] = None

        for index in range(5):
            if guess_chars[index] is not None and guess_chars[index] in solution_chars:
                result[index] = 2
                solution_chars[solution_chars.index(guess_chars[index])] = None

        return result

    def calculate_wordle_feedback(self, guess: str, feedback: list[int]) -> tuple[list[str], list[str], list[str]]:
        correct_position = []
        wrong_position = []
        not_in_word = []

        for index, value in enumerate(feedback):
            letter = guess[index]
            if value == 1:
                correct_position.append(letter)
            elif value == 2:
                wrong_position.append(letter)
            else:
                not_in_word.append(letter)

        return correct_position, wrong_position, not_in_word
