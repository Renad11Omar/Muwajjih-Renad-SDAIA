# Benchmarks

Measurements are recorded from real runs of the current repository and model version.

| Measurement | Result | Notes |
|---|---:|---|
| Synthetic training rows | 192 | `scripts/train_model.py`, fixed seed |
| Model artifact | 86,730 bytes | `models/muwajjih_v1.joblib` |
| Fast test gate | 0.18 s | 22 tests passed, coverage 97.68% |
| Behavioural suite | 0.20 s | 5 behavioural tests passed |
| Docker image build | 7.1 s | `make image`, successful multi-stage build |
| Warm rebuild | 1.4 s | `make up --build`, cached rebuild |
| Docker image size | 102.0 MB | `make image-size` |
| Time-to-ready | 6.8 s | Compose startup until `/v1/ready` |
| Container p99 | 21.9 ms | `hey`, 30 s / 10 concurrent requests |
| Benchmark mean | 0.314 ms | 100 iterations |
| Benchmark p95 | 0.321 ms | 100 iterations |
| Benchmark max | 0.348 ms | 100 iterations |

## Recording rule

Only measurements from the current repository, model version, and local runs are accepted here.
Course-deck example numbers are intentionally not copied into this file.
