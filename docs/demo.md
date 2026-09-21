# 5-minute live demo script

1. `docker compose up -d` and `docker compose ps` — show both services healthy.
2. Send a valid Arabic emergency complaint to `/v1/predict` — show department, urgent priority, model version, reason codes and trace id.
3. Send a malformed request with an extra field — show the unified 422 envelope and trace id.
4. Run the behavioural command — `pytest -m slow -q` — explain invariance, directional emergency rule, and the golden file.
5. Open `.github/workflows/ci.yml` and explain lint/type-check → tests/coverage → image smoke → GHCR publish on main with commit-SHA tagging.
