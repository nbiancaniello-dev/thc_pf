#BUILD STAGE

FROM python:3.14.7 AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.4 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

COPY . ./
RUN uv sync --locked --no-dev

# PRODUCTION STAGE

FROM python:3.14.7

WORKDIR /app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

COPY --from=builder --chown=appuser /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

ENTRYPOINT ["./entrypoint.sh"]
CMD ["/bin/sh", "-c", "exec fastapi run --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]