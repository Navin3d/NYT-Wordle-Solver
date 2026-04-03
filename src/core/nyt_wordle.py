import datetime
import requests

class NYTWordleSolver:
    def __init__(self):
        self.green = chr(0x1F7E9)
        self.yellow = chr(0x1F7E8)
        self.white = chr(0x2B1C)
        self.solution = self._get_solution()

    def _get_solution(self) -> str:
        date = datetime.date.today()
        url = f"https://www.nytimes.com/svc/wordle/v2/{date:%Y-%m-%d}.json"
        # url = f"https://www.nytimes.com/svc/wordle/v2/2026-03-01.json"
        response = requests.get(url).json()
        return response['solution']

    def get_grid(self, num_array):
        # Mapping: 1=Green, 2=Yellow, 0=Gray
        mapping = {1: self.green, 2: self.yellow, 0: self.white}
        return "".join(mapping.get(x, self.white) for x in num_array) + "\n"

    def update_pattern(self, current_pattern: str, guess: str, feedback: list[int]) -> str:
        pattern = list(current_pattern)
        for i, fb in enumerate(feedback):
            if fb == 1:  # Green
                pattern[i] = guess[i]
        return "".join(pattern)

    def attempt(self, guess: str):
        result = [0] * 5
        sol_list = list(self.solution)
        guess_list = list(guess)

        # First pass: Greens
        for i in range(5):
            if guess_list[i] == sol_list[i]:
                result[i] = 1
                sol_list[i] = None
                guess_list[i] = None

        # Second pass: Yellows
        for i in range(5):
            if guess_list[i] is not None and guess_list[i] in sol_list:
                result[i] = 2
                sol_list[sol_list.index(guess_list[i])] = None

        return result

    def calculate_wordle_feedback(self, guess: str, feedback: list[int]):
        right_pos, wrong_pos, not_in_word = [], [], []
        for i, fb in enumerate(feedback):
            if fb == 1:
                right_pos.append(guess[i])
            elif fb == 2:
                wrong_pos.append(guess[i])
            else:
                not_in_word.append(guess[i])
        return right_pos, wrong_pos, not_in_word

    # def get_grid(self, num_array):
    #     grid = ""
    #     for letter in num_array:
    #         if letter == 0:
    #             grid += self.white
    #         elif letter == 1:
    #             grid += self.green
    #         else:
    #             grid += self.yellow
    #     grid += '\n'
    #     return grid
    #
    # def update_pattern(self, pattern: str, guess: str, feedback: list[int]) -> str:
    #     result = list(pattern)
    #     for i, (letter, fb) in enumerate(zip(guess, feedback)):
    #         if fb == 1:  # Green
    #             result[i] = letter
    #     return ''.join(result)
    #
    # def attempt(self, word):
    #     print("Attempting to solve word '{}'".format(word))
    #
    #     # Wordle scoring logic - return array [0=white, 1=yellow, 2=green]
    #     result = [0] * 5  # Initialize all white
    #     letter_count = {}
    #
    #     # Count solution letters
    #     for char in self.solution:
    #         letter_count[char] = letter_count.get(char, 0) + 1
    #
    #     self.solution = self._get_solution()
    #     print("word is: {}".format(word))
    #
    #     # First pass: mark greens (2)
    #     for i, guess_char in enumerate(word):
    #         print(i, guess_char)
    #         if guess_char == self.solution[i]:
    #             result[i] = 1  # Green
    #             letter_count[guess_char] -= 1
    #
    #     # Second pass: mark yellows (1)
    #     for i, guess_char in enumerate(word):
    #         if result[i] == 0 and letter_count.get(guess_char, 0) > 0:
    #             result[i] = 2  # Yellow
    #             letter_count[guess_char] -= 1
    #
    #     return result
    #
    # def calculate_wordle_feedback(self, guess: str, feedback: list[int]) -> tuple[list[str], list[str], list[str]]:
    #     """
    #     Calculate the 3 stateless arrays from a single guess and feedback.
    #
    #     Args:
    #         guess: 5-letter guess string
    #         feedback: [0,1,2] array for each position
    #
    #     Returns:
    #         (letters_in_right_position, letters_in_wrong_position, letters_not_in_word)
    #     """
    #     right_pos = []
    #     wrong_pos = []
    #     not_in_word = []
    #
    #     for letter, fb in zip(guess, feedback):
    #         if fb == 1:  # Green
    #             right_pos.append(letter)
    #         elif fb == 2:  # Yellow
    #             wrong_pos.append(letter)
    #         elif fb == 0:  # White
    #             not_in_word.append(letter)
    #
    #     return right_pos, wrong_pos, not_in_word
