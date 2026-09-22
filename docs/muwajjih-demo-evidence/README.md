# Muwajjih — Demo Evidence

This folder contains the screenshot evidence used for the Muwajjih capstone demonstration.

## 1. Compose & Service Readiness

The screenshots show the Docker Compose stack running and the API health/readiness endpoints returning successful responses.

![Compose healthy](images/01-compose-healthy.png)

![Ready 200](images/02-ready-200.png)

![Health 200](images/03-health-200.png)

## 2. Valid Prediction

A valid municipal complaint is submitted to `POST /v1/predict` and the service returns a structured HTTP 200 response with department, priority, model version, trace ID, and no error.

![Valid prediction](images/04-valid-predict.png)

## 3. Malformed Request & Validation

An invalid request missing the required `text` field is rejected with HTTP 422 and a structured validation error.

![Malformed request](images/05-malformed-request-422.png)

![Validation details](images/05-malformed-request-422-details.png)

## 4. Behavioural Tests

The real behavioural suite passes five selected tests, including invariance, emergency-signal directionality, and a golden-reference test.

![Behavioural tests](images/06-behavioral-tests.png)

## 5. CI/CD & GHCR

The `main` pipeline completes successfully with validation, secret scanning, container smoke testing, behavioural testing, and publishing.

![Green CI](images/07-ci-pipeline-green.png)

![GHCR publish](images/08-ghcr-publish.png)

## Suggested demo order

1. Compose + Health/Ready
2. Valid prediction
3. Malformed request
4. Behavioural test
5. CI/CD and GHCR publication
