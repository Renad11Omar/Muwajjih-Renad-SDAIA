# Engineering Decisions

## 1. Character n-gram TF-IDF + Logistic Regression

We use a lightweight, deterministic scikit-learn stack that handles Arabic and English short text without a deep-learning runtime. It keeps the artifact small enough for a production-style container while remaining easy to inspect and test.

## 2. Policy override for explicit emergencies

The model predicts department and baseline priority, but explicit emergency signals such as fire or gas leak are enforced as deterministic business policy. This prevents a low-confidence model output from suppressing a safety-critical signal and gives us a strong directional behavioural test.

## 3. Model Protocol + dependency injection

The service depends on a stable `TriageModel` Protocol, not on sklearn. This keeps the ML framework at the adapter edge and lets tests inject `ConstantModel` without loading the real artifact.

## 4. Redis is a readiness-gated supporting service

Compose starts Redis first and gates the API on `service_healthy`. The cache is an operational supporting dependency, and the service fails fast during startup when Redis or the model is unavailable rather than serving partially initialized predictions.

## 5. Model baked into the image

The model artifact is copied into its own Docker layer. This makes the deployed artifact self-contained and easy to roll back as a single immutable unit. A future model-registry deployment can replace the adapter without changing the service contract.
