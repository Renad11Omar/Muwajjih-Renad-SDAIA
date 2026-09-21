import hashlib
import json

from muwajjih.domain.entities import Complaint, Department, Priority, TriageDecision
from muwajjih.domain.policies import apply_priority_policy, normalize_text
from muwajjih.service.interfaces import Cache, TriageModel


class TriageScorer:
    """Pure orchestration: normalize -> predict -> policy -> decision."""

    def __init__(self, model: TriageModel, cache: Cache | None = None) -> None:
        self.model = model
        self.cache = cache

    def score(self, complaint: Complaint) -> TriageDecision:
        cache_key = hashlib.sha256(normalize_text(complaint.text).encode("utf-8")).hexdigest()
        if self.cache is not None:
            cached = self.cache.get(cache_key)
            if cached is not None:
                payload = json.loads(cached)
                return TriageDecision(
                    complaint_id=complaint.complaint_id,
                    department=Department(payload["department"]),
                    priority=Priority(payload["priority"]),
                    confidence=float(payload["confidence"]),
                    model_version=payload["model_version"],
                    reason_codes=tuple(payload["reason_codes"]),
                )

        raw = self.model.predict(Complaint(complaint.complaint_id, normalize_text(complaint.text)))
        priority, policy_reasons = apply_priority_policy(raw, complaint.text)
        confidence = min(raw.department_confidence, raw.priority_confidence)
        reason_codes = ("MODEL_DEPARTMENT",) + policy_reasons
        decision = TriageDecision(
            complaint_id=complaint.complaint_id,
            department=raw.department,
            priority=priority,
            confidence=confidence,
            model_version=raw.model_version,
            reason_codes=reason_codes,
        )
        if self.cache is not None:
            self.cache.set(
                cache_key,
                json.dumps(
                    {
                        "department": decision.department.value,
                        "priority": decision.priority.value,
                        "confidence": decision.confidence,
                        "model_version": decision.model_version,
                        "reason_codes": decision.reason_codes,
                    },
                    ensure_ascii=False,
                ),
            )
        return decision
