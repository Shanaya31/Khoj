"""Pydantic models shared by the API, the city-pack loader and the LLM layer."""

from typing import Literal

from pydantic import BaseModel, Field

Interest = Literal[
    "history", "architecture", "nature", "art", "local_life", "hidden_details", "surprise"
]
Duration = Literal[20, 45, 90, 120]  # 120 means "2+ hours"


class MissionRequest(BaseModel):
    city: str = "mumbai"
    area: str | None = None
    duration_minutes: Duration = 45
    interest: Interest = "surprise"


class Objective(BaseModel):
    text: str = Field(min_length=3, max_length=300)
    place_id: str | None = None
    fact_ids: list[str] = Field(default_factory=list)


class Mission(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    intro: str = ""
    objectives: list[Objective] = Field(min_length=3, max_length=6)
    closing: str = ""


class MissionResponse(BaseModel):
    session_id: str
    city: str
    area: str | None
    duration_minutes: int
    interest: str
    mission: Mission
    source: Literal["gemma", "curated"]


class ObservationRequest(BaseModel):
    session_id: str
    text: str = Field(min_length=1, max_length=1000)
    question: str | None = Field(default=None, max_length=500)
    lat: float | None = None
    lon: float | None = None


class ObservationResponse(BaseModel):
    id: str
    session_id: str
    text: str
    question: str | None
    explanation: str | None
    fact_ids: list[str]
    created_at: str


class ReflectionRequest(BaseModel):
    session_id: str


class Journal(BaseModel):
    title: str
    minutes: int
    observation_count: int
    discoveries: list[str]
    story: str


class ReflectionResponse(BaseModel):
    session_id: str
    journal: Journal
    source: Literal["gemma", "template"]
