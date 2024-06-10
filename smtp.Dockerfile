FROM python:3.9-slim

WORKDIR /app

COPY requirements-smtp.txt .

RUN pip install --no-cache-dir -r requirements-smtp.txt

COPY mock_smtp.py .

RUN useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8025

CMD ["uvicorn", "mock_smtp:app", "--host", "0.0.0.0", "--port", "8025"]
