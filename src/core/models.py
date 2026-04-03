from typing import TypedDict, Annotated
from operator import sub, concat, add
from pydantic import BaseModel, Field, field_validator


class WordleState(TypedDict):
    word: str
    attempted_words: Annotated[list[str], add]
    attempted_words_results: Annotated[list[list[int]], add]
    forbidden_locations: dict[str, list[int]]
    letters_in_wrong_position: list[str]
    letters_not_in_word: list[str]
    remaining_attempts: Annotated[int, add]
    solved: bool
    solution_grid: Annotated[str, ""]


class GuessResponse(BaseModel):
    word: str = Field(description="The guessing new word will should be parsed in here.", default="")
    meaning: str = Field(description="The meaning of the guessing word.", default="")
    reasoning: str = Field(description="The reasoning of the guessing word.", default="")

    @field_validator("word")
    @classmethod
    def enforce_five_letters(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) != 5:
            raise ValueError(f"word must be exactly 5 letters, got '{v}' ({len(v)} letters)")
        if not v.isalpha():
            raise ValueError(f"word must contain only letters, got '{v}'")
        return v
