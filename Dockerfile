FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y build-essential libc6-dev \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY app /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
