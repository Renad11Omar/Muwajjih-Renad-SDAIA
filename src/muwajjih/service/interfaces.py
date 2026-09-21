from typing import Protocol

from muwajjih.domain.entities import Complaint, RawPrediction


class TriageModel(Protocol):
    model_version: str

    def predict(self, complaint: Complaint) -> RawPrediction: ...


class Cache(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl_seconds: int = 300) -> None: ...

    def ping(self) -> bool: ...

    def close(self) -> None: ...
