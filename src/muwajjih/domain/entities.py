from dataclasses import dataclass
from enum import StrEnum


class Department(StrEnum):
    ROADS = "roads"
    WATER = "water"
    WASTE = "waste"
    ELECTRICITY = "electricity"
    PUBLIC_SAFETY = "public_safety"
    PERMITS = "permits"


class Priority(StrEnum):
    NORMAL = "normal"
    URGENT = "urgent"


@dataclass(frozen=True)
class Complaint:
    complaint_id: str
    text: str


@dataclass(frozen=True)
class RawPrediction:
    department: Department
    department_confidence: float
    priority: Priority
    priority_confidence: float
    model_version: str


@dataclass(frozen=True)
class TriageDecision:
    complaint_id: str
    department: Department
    priority: Priority
    confidence: float
    model_version: str
    reason_codes: tuple[str, ...]
