from pathlib import Path
from typing import Any

import joblib

from muwajjih.domain.entities import Complaint, Department, Priority, RawPrediction


class SklearnMuwajjihModel:
    def __init__(self, bundle: dict[str, Any], model_version: str) -> None:
        self._department_model = bundle["department_model"]
        self._priority_model = bundle["priority_model"]
        self.model_version = model_version

    @classmethod
    def load(cls, path: str | Path, model_version: str) -> "SklearnMuwajjihModel":
        bundle = joblib.load(path)
        return cls(bundle=bundle, model_version=model_version)

    def predict(self, complaint: Complaint) -> RawPrediction:
        text = [complaint.text]
        department_probs = self._department_model.predict_proba(text)[0]
        priority_probs = self._priority_model.predict_proba(text)[0]
        department_index = int(department_probs.argmax())
        priority_index = int(priority_probs.argmax())
        department = Department(self._department_model.classes_[department_index])
        priority = Priority(self._priority_model.classes_[priority_index])
        return RawPrediction(
            department=department,
            department_confidence=float(department_probs[department_index]),
            priority=priority,
            priority_confidence=float(priority_probs[priority_index]),
            model_version=self.model_version,
        )

    def warmup(self) -> None:
        self.predict(Complaint("MWJ-WARMUP", "بلاغ عن تسرب مياه في شارع سكني"))
