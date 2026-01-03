from typing import TypedDict, Annotated
from operator import sub, concat, add
from pydantic import BaseModel, Field


class WordleState(TypedDict):
    attempted_words: Annotated[list[str], add]
    letters_in_right_position: list[str]
    letters_in_wrong_position: list[str]
    letters_not_in_word: list[str]
    remaining_attempts: Annotated[int, add]
    solved: bool
    solution_grid: Annotated[str, ""]


class GuessResponse(BaseModel):
    word: str = Field(description="The guessing new word will should be parsed in here.", default="")
    meaning: str = Field(description="The meaning of the guessing word.", default="")
    reasoning: str = Field(description="The reasoning of the guessing word.", default="")
