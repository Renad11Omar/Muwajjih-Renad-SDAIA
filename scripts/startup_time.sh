#!/usr/bin/env bash
set -euo pipefail

start=$(python - <<'PY'
import time
print(time.time())
PY
)
docker compose up -d
for _ in $(seq 1 60); do
  if curl -fsS http://localhost:8000/v1/ready >/dev/null 2>&1; then
    end=$(python - <<'PY'
import time
print(time.time())
PY
)
    python - <<PY
print(f"time_to_ready_s={float('$end')-float('$start'):.3f}")
PY
    exit 0
  fi
  sleep 0.2
done
echo "service did not become ready within 12 seconds" >&2
exit 1
