import csv
from pathlib import Path

import pytest

from muwajjih.domain.entities import Complaint, Priority
from muwajjih.service.scorer import TriageScorer

pytestmark = [pytest.mark.behavioural, pytest.mark.slow]


def _score(real_model, complaint_id: str, text: str):
    return TriageScorer(real_model).score(Complaint(complaint_id, text))


@pytest.mark.parametrize(
    "text",
    [
        "water pipe is leaking in the neighborhood",
        "street pavement is cracked and damaged",
        "how can I renew my shop permit",
    ],
)
def test_invariance_to_casing_and_whitespace(real_model, text):
    base = _score(real_model, "MWJ-BHV-001", text)
    noisy = _score(real_model, "MWJ-BHV-001", f"   {text.upper()}   ")
    assert noisy.department == base.department
    assert noisy.priority == base.priority
    assert noisy.confidence == pytest.approx(base.confidence, abs=1e-12)


def test_directional_emergency_signal_never_lowers_priority(real_model):
    normal = _score(real_model, "MWJ-BHV-002", "street service issue near houses")
    urgent = _score(real_model, "MWJ-BHV-003", "street service issue near houses; fire emergency")
    assert normal.priority is Priority.NORMAL
    assert urgent.priority is Priority.URGENT


def test_golden_reference(real_model):
    root = Path(__file__).resolve().parents[2]
    golden = root / "models" / "golden_scores_v1.csv"
    with golden.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            decision = _score(real_model, row["complaint_id"], row["text"])
            assert decision.department.value == row["department"], row["complaint_id"]
            assert decision.priority.value == row["priority"], row["complaint_id"]
            assert decision.confidence == pytest.approx(float(row["confidence"]), abs=1e-6)
