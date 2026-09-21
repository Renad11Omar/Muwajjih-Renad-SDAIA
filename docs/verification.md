# Verification status

## Verified in the build environment

- `22` fast unit/integration tests pass.
- `5` behavioural/golden tests pass against the real model artifact.
- Branch coverage over domain/service/api is `97.69%` in the current validation environment, above the 80% course gate.
- `python -m compileall` passes for source, tests and scripts.
- The custom architecture guard passes: `architecture_check_ok`.
- Git history contains 7 logical commits on `main`.
- `git diff --check` is clean.

## Requires a real Docker/GitHub environment

- Docker image build and final image-size measurement.
- Compose startup, Redis health gate, `/ready` healthcheck and smoke test.
- Warm rebuild timing and containerised p99 benchmark.
- `ruff`, `mypy`, and official `import-linter` execution (the current build environment does not have these executables and has no outbound package network).
- GitHub Actions green run, GHCR publication, and actual branch-protection settings.

The project deliberately does not invent those external measurements.
