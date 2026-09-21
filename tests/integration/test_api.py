import pytest

from muwajjih.domain.entities import Department, Priority
from tests.helpers import ConstantModel


@pytest.mark.integration
def test_predict_contract_and_trace_id(client_factory):
    with client_factory(
        ConstantModel(department=Department.WATER, priority=Priority.NORMAL)
    ) as client:
        response = client.post(
            "/v1/predict",
            json={"complaint_id": "MWJ-IT-001", "text": "water pipe is leaking"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["department"] == "water"
    assert body["data"]["priority"] == "normal"
    assert body["trace_id"]
    assert response.headers["X-Trace-Id"] == body["trace_id"]


@pytest.mark.integration
def test_unknown_field_is_rejected(client_factory):
    with client_factory() as client:
        response = client.post(
            "/v1/predict",
            json={"complaint_id": "MWJ-IT-002", "text": "road damage", "secret": "nope"},
        )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
def test_length_validation_is_rejected(client_factory):
    with client_factory() as client:
        response = client.post(
            "/v1/predict",
            json={"complaint_id": "MWJ-IT-003", "text": "x"},
        )
    assert response.status_code == 422
    assert response.json()["data"] is None


@pytest.mark.integration
def test_ready_returns_503_before_startup(client_factory):
    with client_factory(ready=False) as client:
        response = client.get("/v1/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_ERROR"
    assert response.headers["Retry-After"] == "5"


@pytest.mark.integration
def test_internal_error_has_no_stack_trace(client_factory):
    class ExplodingScorer:
        def score(self, complaint):
            raise RuntimeError("secret stack detail")

    with client_factory(scorer=ExplodingScorer()) as client:
        response = client.post(
            "/v1/predict",
            json={"complaint_id": "MWJ-IT-004", "text": "power is out"},
        )
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "secret stack detail" not in response.text


@pytest.mark.integration
def test_batch_extension_respects_contract(client_factory):
    with client_factory() as client:
        response = client.post(
            "/v1/predictions:batch",
            json={
                "items": [
                    {"complaint_id": "MWJ-B-001", "text": "road pothole near school"},
                    {"complaint_id": "MWJ-B-002", "text": "water pipe leaking"},
                ]
            },
        )
    assert response.status_code == 200
    assert len(response.json()["data"]) == 2

@pytest.mark.integration
def test_health_and_forwarded_trace_id(client_factory):
    with client_factory() as client:
        response = client.get(
            "/v1/health",
            headers={"X-Trace-Id": "9f3e0f5f-7b3b-4d0f-8f8c-123456789abc"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Trace-Id"] == "9f3e0f5f-7b3b-4d0f-8f8c-123456789abc"


@pytest.mark.integration
def test_invalid_trace_id_is_replaced(client_factory):
    with client_factory() as client:
        response = client.get("/v1/health", headers={"X-Trace-Id": "not-a-uuid"})
    assert response.status_code == 200
    assert response.headers["X-Trace-Id"] != "not-a-uuid"


@pytest.mark.integration
def test_predict_without_scorer_returns_503():
    from fastapi.testclient import TestClient
    from muwajjih.api.app import create_app

    app = create_app(enable_lifespan=False)
    app.state.started_at = "test"
    app.state.ready = True
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/v1/predict", json={"complaint_id": "MWJ-IT-005", "text": "road damage"}
        )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_ERROR"

@pytest.mark.integration
def test_lifespan_loads_model_and_checks_cache(monkeypatch):
    from fastapi.testclient import TestClient
    import muwajjih.api.app as app_module

    class FakeLoadedModel(ConstantModel):
        model_version = "muwajjih-test"

        def warmup(self):
            return None

    class FakeRedis:
        def __init__(self, url):
            self.url = url
        def ping(self):
            return True
        def get(self, key):
            return None
        def set(self, key, value, ttl_seconds=300):
            return None
        def close(self):
            return None

    monkeypatch.setattr(
        app_module.SklearnMuwajjihModel, "load", lambda path, version: FakeLoadedModel()
    )
    monkeypatch.setattr(app_module, "RedisCache", FakeRedis)
    app = app_module.create_app(enable_lifespan=True)
    with TestClient(app) as client:
        response = client.get("/v1/ready")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ready"

@pytest.mark.integration
def test_malformed_corpus_rejected(client_factory):
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    payloads = sorted((root / "payloads" / "malformed").glob("*.json"))
    with client_factory() as client:
        for payload in payloads:
            response = client.post(
                "/v1/predict",
                content=payload.read_bytes(),
                headers={"content-type": "application/json"},
            )
            assert 400 <= response.status_code < 500, payload.name
            assert response.json()["data"] is None
            assert response.json()["trace_id"]
            json.loads(response.text)


@pytest.mark.integration
def test_batch_extension_is_bounded(client_factory):
    items = [
        {"complaint_id": f"MWJ-B-{i:03d}", "text": "road pothole near school"}
        for i in range(33)
    ]
    with client_factory() as client:
        response = client.post("/v1/predictions:batch", json={"items": items})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
