FROM python:3.14.2-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev

COPY backend /app/backend

RUN adduser --disabled-password --gecos "" app \
    && chown -R app:app /app

USER app

WORKDIR /app/backend

RUN python -m uvicorn --version

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
