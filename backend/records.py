"""Validated, reviewable record proposals; extraction never writes business state."""
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskItem(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, max_length=1000)
    instructions: str = Field(min_length=1, max_length=2000)
    minutes: int = Field(strict=True, ge=1, le=10080)
    evidence: str = Field(min_length=1, max_length=1000)
    acceptance: str = Field(min_length=1, max_length=1000)


class ClueProposal(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    category: str = Field(min_length=1, max_length=50)
    content: str = Field(min_length=1, max_length=2000)
    source: Literal['self_reported', 'assistant_inferred']
    quote: str = Field(min_length=1, max_length=2000)


class ClueProposals(BaseModel):
    model_config = ConfigDict(extra='forbid')
    items: list[ClueProposal] = Field(max_length=12)


def decode_proposal(text: str) -> dict:
    text = text.strip()
    if text.startswith('```') and text.endswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    result = json.loads(text)
    if not isinstance(result, dict):
        raise ValueError('Expected object')
    return result
