# Capstone requirement traceability

This file maps the course capstone requirements to concrete repository evidence.

| Requirement | Evidence in Muwajjih |
|---|---|
| Clean `src` layout | `src/muwajjih/domain`, `service`, `adapters`, `api` |
| Model Protocol + DI | `src/muwajjih/service/interfaces.py`, `api/routes.py`, `tests/helpers.py` |
| Architecture contract | `pyproject.toml` import-linter contracts; `make arch` |
| Unified Makefile interface | `Makefile` targets: install/test/lint/image/smoke (+ typecheck/arch) |
| `POST /v1/predict` | `src/muwajjih/api/routes.py` |
| Unified envelope + trace id | `src/muwajjih/api/schemas.py`, `app.py` middleware/error handlers |
| Strict validation | Pydantic `extra="forbid"`, length and ID constraints |
| Startup load + warm-up | FastAPI lifespan in `src/muwajjih/api/app.py` |
| `/health` vs `/ready` | `routes.py`; `/health` is liveness, `/ready` checks startup state |
| Multi-stage image + non-root | `Dockerfile` |
| `/ready` healthcheck | `Dockerfile`, `docker-compose.yml` |
| Supporting service + health gate | Redis `feature-cache`, `service_healthy` in `docker-compose.yml` |
| Unit / integration / behavioural | `tests/unit`, `tests/integration`, `tests/behavioural` |
| Invariance | `test_invariance_to_casing_and_whitespace` |
| Directional | `test_directional_emergency_signal_never_lowers_priority` |
| Golden file | `models/golden_scores_v1.csv`, `test_golden_reference` |
| Branch coverage gate | `pyproject.toml` + `pytest --cov-branch` |
| CI/CD | `.github/workflows/ci.yml` |
| Main-only publish | publish job checks `push` to `main` |
| Commit-SHA image tag | `ghcr.io/${{ github.repository }}:${{ github.sha }}` |
| Secrets scan | Gitleaks job |
| Typed config | `src/muwajjih/config.py` |
| Structured JSON logs | `src/muwajjih/api/logging_setup.py` |
| README runbook | `README.md` |
| Benchmarks | `BENCHMARKS.md`, `scripts/benchmarks.py` |
| Five engineering decisions | `DECISIONS.md` |
| Extension | bounded `POST /v1/predictions:batch` |
| Live demo | `docs/demo.md` |

## External actions still required after repository creation

The source tree can define the CI workflow and branch-protection checklist, but GitHub must be configured for the actual repository: enable required checks on `main`, require at least one review, and disable force-push. A real green CI run and GHCR publication also require pushing this repository to GitHub.
