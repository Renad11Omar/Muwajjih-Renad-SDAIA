from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from muwajjih.domain.entities import Department, Priority


class ComplaintRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    complaint_id: str = Field(pattern=r"^MWJ-[A-Z0-9-]{3,40}$")
    text: str = Field(min_length=5, max_length=500)


class DecisionData(BaseModel):
    complaint_id: str
    department: Department
    priority: Priority
    confidence: float = Field(ge=0, le=1)
    model_version: str
    reason_codes: list[str]


class ErrorData(BaseModel):
    code: str
    message: str
    details: list[dict[str, str]] = Field(default_factory=list)


class Envelope[T](BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: UUID
    data: T | None = None
    error: ErrorData | None = None


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ComplaintRequest] = Field(min_length=1, max_length=32)
