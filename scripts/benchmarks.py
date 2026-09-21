from __future__ import annotations

import statistics
import time
from pathlib import Path

from muwajjih.adapters.sklearn_model import SklearnMuwajjihModel
from muwajjih.domain.entities import Complaint
from muwajjih.service.scorer import TriageScorer

root = Path(__file__).resolve().parents[1]
model = SklearnMuwajjihModel.load(root / "models" / "muwajjih_v1.joblib", "muwajjih-v1")
scorer = TriageScorer(model)

samples = [
    Complaint("MWJ-BENCH-001", "road pothole near school"),
    Complaint("MWJ-BENCH-002", "انقطاع المياه في الحي"),
    Complaint("MWJ-BENCH-003", "fire near the public park"),
]

for sample in samples:
    scorer.score(sample)
times = []
for i in range(100):
    sample = samples[i % len(samples)]
    t0 = time.perf_counter()
    scorer.score(sample)
    times.append((time.perf_counter() - t0) * 1000)
print(f"iterations=100")
print(f"mean_ms={statistics.mean(times):.3f}")
print(f"p95_ms={sorted(times)[94]:.3f}")
print(f"max_ms={max(times):.3f}")
print(f"model_bytes={(root/'models/muwajjih_v1.joblib').stat().st_size}")
