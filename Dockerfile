# ---------- Stage 1: builder ----------
FROM python:3.12-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# Dependency layer: changes rarely, so code edits reuse this cache.
COPY requirements.lock .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir --no-compile --target /opt/venv/lib/python3.12/site-packages -r requirements.lock

COPY pyproject.toml README.md ./
COPY src/ src/
RUN /opt/venv/bin/pip install --no-cache-dir --no-compile --no-deps --target /opt/venv/lib/python3.12/site-packages .

# Remove test payloads/bytecode that are not needed at runtime.
RUN find /opt/venv/lib/python3.12/site-packages -type d \( -name tests -o -name test -o -name __pycache__ \) -prune -exec rm -rf {} + \
    && find /opt/venv/lib/python3.12/site-packages -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime
RUN useradd --create-home --uid 10001 appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY models/muwajjih_v1.joblib /models/muwajjih_v1.joblib

ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH="/app/src" \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/v1/ready', timeout=2)" || exit 1

CMD ["python", "-m", "uvicorn", "muwajjih.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
