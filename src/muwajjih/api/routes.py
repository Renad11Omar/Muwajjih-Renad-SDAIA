from typing import Annotated, Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request

from muwajjih.adapters.redis_cache import RedisCache
from muwajjih.adapters.sklearn_model import SklearnMuwajjihModel
from muwajjih.api.schemas import BatchRequest, ComplaintRequest, DecisionData, Envelope
from muwajjih.config import Settings
from muwajjih.domain.entities import Complaint
from muwajjih.service.scorer import TriageScorer

router = APIRouter(tags=["triage"])


def set_dependencies(
    app: FastAPI, model: SklearnMuwajjihModel, cache: RedisCache, settings: Settings
) -> None:
    app.state.model = model
    app.state.cache = cache
    app.state.settings = settings
    app.state.scorer = TriageScorer(model, cache)


def get_scorer(request: Request) -> TriageScorer:
    scorer = getattr(request.app.state, "scorer", None)
    if scorer is None:
        raise HTTPException(
            status_code=503, detail="Service not ready", headers={"Retry-After": "5"}
        )
    return scorer


@router.get("/health")
def health(request: Request) -> dict[str, Any]:
    return {"status": "ok", "service": "muwajjih", "started_at": request.app.state.started_at}


@router.get("/ready", response_model=Envelope[dict[str, str]])
def ready(request: Request) -> Envelope[dict[str, str]]:
    if not getattr(request.app.state, "ready", False):
        raise HTTPException(
            status_code=503, detail="Service not ready", headers={"Retry-After": "5"}
        )
    return Envelope(trace_id=request.state.trace_id, data={"status": "ready"})


@router.post("/predict", response_model=Envelope[DecisionData])
def predict(
    body: ComplaintRequest,
    request: Request,
    scorer: Annotated[TriageScorer, Depends(get_scorer)],
) -> Envelope[DecisionData]:
    decision = scorer.score(Complaint(body.complaint_id, body.text))
    return Envelope(
        trace_id=request.state.trace_id,
        data=DecisionData(
            complaint_id=decision.complaint_id,
            department=decision.department,
            priority=decision.priority,
            confidence=decision.confidence,
            model_version=decision.model_version,
            reason_codes=list(decision.reason_codes),
        ),
    )


@router.post("/predictions:batch", response_model=Envelope[list[DecisionData]])
def predict_batch(
    body: BatchRequest,
    request: Request,
    scorer: Annotated[TriageScorer, Depends(get_scorer)],
) -> Envelope[list[DecisionData]]:
    items = []
    for complaint in body.items:
        decision = scorer.score(Complaint(complaint.complaint_id, complaint.text))
        items.append(
            DecisionData(
                complaint_id=decision.complaint_id,
                department=decision.department,
                priority=decision.priority,
                confidence=decision.confidence,
                model_version=decision.model_version,
                reason_codes=list(decision.reason_codes),
            )
        )
    return Envelope(trace_id=request.state.trace_id, data=items)
