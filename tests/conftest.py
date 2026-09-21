from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from muwajjih.adapters.sklearn_model import SklearnMuwajjihModel
from muwajjih.api.app import create_app
from muwajjih.api.routes import get_scorer
from muwajjih.domain.entities import Complaint
from muwajjih.service.scorer import TriageScorer


from tests.helpers import ConstantModel, FakeCache



@pytest.fixture
def client_factory():
    def _make(
        model: ConstantModel | None = None,
        scorer: TriageScorer | None = None,
        *,
        ready: bool = True,
    ) -> TestClient:
        app = create_app(enable_lifespan=False)
        app.state.started_at = "test"
        app.state.ready = ready
        actual_scorer = scorer or TriageScorer(model or ConstantModel())
        app.dependency_overrides[get_scorer] = lambda: actual_scorer
        return TestClient(app, raise_server_exceptions=False)

    return _make


@pytest.fixture(scope="session")
def real_model():
    root = Path(__file__).resolve().parents[1]
    return SklearnMuwajjihModel.load(root / "models" / "muwajjih_v1.joblib", "muwajjih-v1")


@pytest.fixture
def sample_complaint() -> Complaint:
    return Complaint("MWJ-TEST-001", "حفرة كبيرة في الشارع قرب المدرسة")
