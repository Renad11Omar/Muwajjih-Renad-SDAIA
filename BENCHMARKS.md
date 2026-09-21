# Benchmarks

Measurements are recorded from real runs, not copied from the course deck.

| Measurement | Result | Notes |
|---|---:|---|
| Synthetic training rows | 192 | `scripts/train_model.py`, fixed seed |
| Model artifact | 86,730 bytes | `models/muwajjih_v1.joblib` |
| Fast test gate | 0.21 s | 22 fast tests; 98% branch coverage in validation environment |
| Slow behavioural suite | 0.77 s | 5 behavioural tests; real artifact + golden reference |
| Docker image size | run locally | `make image && make image-size` |
| Warm rebuild | run locally | edit one `routes.py` line, rebuild, record cache hit/time |
| Time-to-ready | run locally | `scripts/startup_time.sh` or compose timing |
| Container p99 | run locally | `hey -z 30s -c 10` against `/v1/predict` |

## Recording rule

Only measurements from the current repository, model version and local run are accepted here. Course-deck example numbers are intentionally not copied into this file.
