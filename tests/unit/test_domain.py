import pytest

from muwajjih.domain.entities import Complaint, Department, Priority, RawPrediction
from muwajjih.domain.policies import (
    apply_priority_policy,
    contains_emergency_signal,
    normalize_text,
)


@pytest.mark.unit
def test_normalize_text_collapses_whitespace_and_case():
    assert normalize_text("  FIRE   Risk ") == "fire risk"


@pytest.mark.unit
def test_emergency_signal_detects_arabic_and_english():
    assert contains_emergency_signal("بلاغ عن حريق")
    assert contains_emergency_signal("gas leak near the school")
    assert not contains_emergency_signal("pothole near the school")


@pytest.mark.unit
@pytest.mark.parametrize(
    "priority,text,expected",
    [
        (Priority.NORMAL, "حفرة في الطريق", Priority.NORMAL),
        (Priority.NORMAL, "حريق في مبنى", Priority.URGENT),
        (Priority.URGENT, "مشكلة كهرباء", Priority.URGENT),
    ],
)
def test_emergency_policy(priority, text, expected):
    raw = RawPrediction(Department.ROADS, 0.9, priority, 0.8, "test-1")
    decision, reasons = apply_priority_policy(raw, text)
    assert decision is expected
    assert ("EMERGENCY_POLICY_OVERRIDE" in reasons) == contains_emergency_signal(text)


@pytest.mark.unit
def test_complaint_is_immutable(sample_complaint):
    with pytest.raises(Exception):
        sample_complaint.text = "changed"

@pytest.mark.unit
def test_json_logging_formatter_emits_trace_id():
    import json
    import logging
    from muwajjih.api.logging_setup import JsonFormatter

    record = logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None)
    record.trace_id = "abc"
    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "hello"
    assert payload["trace_id"] == "abc"
