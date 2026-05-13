FROM python:3.13-slim AS builder

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml ./

RUN poetry config virtualenvs.in-project true \
    && poetry install --no-root --only main


FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8001

CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8001
