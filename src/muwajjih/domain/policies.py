import re

from muwajjih.domain.entities import Priority, RawPrediction

EMERGENCY_TERMS = (
    "fire",
    "gas leak",
    "smoke",
    "حريق",
    "تسرب غاز",
    "تسرب الغاز",
    "دخان",
    "انفجار",
    "explosion",
)

_SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize semantically neutral formatting while preserving meaningful words."""
    return _SPACE_RE.sub(" ", text.strip().casefold())


def contains_emergency_signal(text: str) -> bool:
    normalized = normalize_text(text)
    return any(term.casefold() in normalized for term in EMERGENCY_TERMS)


def apply_priority_policy(
    raw: RawPrediction, complaint_text: str
) -> tuple[Priority, tuple[str, ...]]:
    """Apply deterministic business policy after model inference."""
    if contains_emergency_signal(complaint_text):
        return Priority.URGENT, ("EMERGENCY_POLICY_OVERRIDE", "MODEL_PRIORITY")
    return raw.priority, ("MODEL_PRIORITY",)
