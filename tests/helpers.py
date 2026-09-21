from dataclasses import dataclass

from muwajjih.domain.entities import Complaint, Department, Priority, RawPrediction


class ConstantModel:
    def __init__(
        self,
        department: Department = Department.ROADS,
        priority: Priority = Priority.NORMAL,
        department_confidence: float = 0.9,
        priority_confidence: float = 0.9,
    ) -> None:
        self.model_version = "test-1"
        self.department = department
        self.priority = priority
        self.department_confidence = department_confidence
        self.priority_confidence = priority_confidence

    def predict(self, complaint: Complaint) -> RawPrediction:
        return RawPrediction(
            department=self.department,
            department_confidence=self.department_confidence,
            priority=self.priority,
            priority_confidence=self.priority_confidence,
            model_version=self.model_version,
        )


@dataclass
class FakeCache:
    values: dict[str, str]

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        self.values[key] = value

    def ping(self) -> bool:
        return True

    def close(self) -> None:
        return None
