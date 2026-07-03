# NOTE: base image / torch install must be swapped for a ROCm-compatible build
# when deploying on the AMD Developer Cloud GPU instance - see README.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY router/ router/
COPY eval/ eval/
COPY service/ service/

EXPOSE 8000

CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
