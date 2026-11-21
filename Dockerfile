FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --index-url https://pypi.org/simple -r requirements.txt

RUN groupadd --system app && \
    useradd --system --gid app --create-home app

COPY --chown=app:app config/ ./config/
COPY --chown=app:app monitoring/ ./monitoring/

RUN mkdir -p /app/logs && chown app:app /app/logs

USER app

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-m", "monitoring.health"]

CMD ["python", "-m", "monitoring.system_monitor"]
