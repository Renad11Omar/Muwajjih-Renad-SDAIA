# Remaining User Actions

Everything that can be completed and verified without your personal accounts or Docker/GitHub access is already in the repository. The remaining actions are only the external environment steps below.

## 1. Verify the final container locally

Run from the repository root:

```bash
make image
make image-size
make up
docker compose ps
make smoke
./scripts/startup_time.sh
```

Then run the load test from your machine:

```bash
hey -z 30s -c 10 -m POST -T "application/json" \
  -d '{"complaint_id":"MWJ-LOAD-001","text":"هناك حريق قرب مدرسة"}' \
  http://localhost:8000/v1/predict
```

Record the actual image size, warm rebuild time, time-to-ready, and container p99 in `BENCHMARKS.md`.

## 2. Create the GitHub repository and push

Create an empty GitHub repository, add it as `origin`, and push `main`.

```bash
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

After pushing, wait for the `CI` workflow to finish green.

## 3. Configure `main` branch protection

In GitHub repository settings for `main`:

- require a pull request before merging
- require at least 1 approving review
- require the CI checks to pass
- disable force pushes
- keep direct pushes restricted so the required-review rule is meaningful

## 4. Final acceptance check

Before submission, verify that GitHub shows a green `CI` run, the image exists in GHCR with the commit SHA tag, and the live demo follows `docs/demo.md`.
