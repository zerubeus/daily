FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mock_smtp.py .

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8025
CMD ["uvicorn", "mock_smtp:app", "--host", "0.0.0.0", "--port", "8025"]
