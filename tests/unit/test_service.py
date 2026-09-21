import pytest

from muwajjih.domain.entities import Department, Priority
from muwajjih.service.scorer import TriageScorer
from tests.helpers import ConstantModel, FakeCache


@pytest.mark.unit
def test_scorer_orchestrates_model_and_policy(sample_complaint):
    scorer = TriageScorer(ConstantModel(department=Department.WATER, priority=Priority.NORMAL))
    decision = scorer.score(sample_complaint)
    assert decision.department is Department.WATER
    assert decision.priority is Priority.NORMAL
    assert decision.reason_codes[0] == "MODEL_DEPARTMENT"


@pytest.mark.unit
def test_scorer_applies_emergency_override():
    from muwajjih.domain.entities import Complaint

    scorer = TriageScorer(ConstantModel(priority=Priority.NORMAL))
    decision = scorer.score(Complaint("MWJ-TEST-002", "fire risk at building"))
    assert decision.priority is Priority.URGENT


@pytest.mark.unit
def test_scorer_cache_roundtrip(sample_complaint):
    cache = FakeCache({})
    scorer = TriageScorer(ConstantModel(department=Department.WASTE), cache)
    first = scorer.score(sample_complaint)
    second = scorer.score(sample_complaint)
    assert first.department is Department.WASTE
    assert second.department is Department.WASTE
    assert second.complaint_id == sample_complaint.complaint_id
