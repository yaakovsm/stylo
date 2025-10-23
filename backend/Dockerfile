# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
  CMD python - <<'PY' || exit 1
import sys, urllib.request
try:
    urllib.request.urlopen("http://localhost:8000/", timeout=2)
    sys.exit(0)
except Exception:
    sys.exit(1)
PY

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
