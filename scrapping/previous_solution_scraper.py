import requests
from bs4 import BeautifulSoup
import json

url = "https://wordfinder.yourdictionary.com/wordle/answers/"
html = requests.get(url).text

soup = BeautifulSoup(html, "html.parser")

# Find all table rows that contain answers
rows = soup.select("table tr")

answers = []
for row in rows:
    cols = row.find_all("td")
    if len(cols) >= 3:
        word = cols[2].text.strip()
        if word and word.isalpha() and len(word) == 5:
            answers.append(word.upper())

# Remove duplicates (if any)
answers = list(dict.fromkeys(answers))

# Save to JSON
with open("wordle_answers.json", "w") as f:
    json.dump(answers, f, indent=2)

print(f"Total answers scraped: {len(answers)}")