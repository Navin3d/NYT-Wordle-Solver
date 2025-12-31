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
        response = requests.get(url).json()
        return response['solution']

    def get_grid(self, num_array):
        grid = ""
        for letter in num_array:
            if letter == 0:
                grid += self.white
            elif letter == 1:
                grid += self.green
            else:
                grid += self.yellow
        grid += '\n'
        return grid

    def attempt(self, word):
        print("Attempting to solve word '{}'".format(word))

        # Wordle scoring logic - return array [0=white, 1=yellow, 2=green]
        result = [0] * 5  # Initialize all white
        letter_count = {}

        # Count solution letters
        for char in self.solution:
            letter_count[char] = letter_count.get(char, 0) + 1

        # First pass: mark greens (2)
        for i, guess_char in enumerate(word):
            if guess_char == self.solution[i]:
                result[i] = 1  # Green
                letter_count[guess_char] -= 1

        # Second pass: mark yellows (1)
        for i, guess_char in enumerate(word):
            if result[i] == 0 and letter_count.get(guess_char, 0) > 0:
                result[i] = 2  # Yellow
                letter_count[guess_char] -= 1

        return result
