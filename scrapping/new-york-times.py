keyboard = [
	['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
	['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
	['enter', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
]

def _find_char_position(char):
     for row_idx, row in enumerate(keyboard):
        if char in row:
            col_idx = row.index(char)
            return (row_idx, col_idx)
     return None

def find_key_xpath(char: str) -> str:
	row, col = _find_char_position(char)
	return f"/html/body/div[2]/div[1]/div[4]/main/div[2]/div[{row + 1}]/button[{col + 1}]"
