FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends adduser && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 -s /bin/bash celeryuser
WORKDIR /app
# Install uv
RUN pip install uv
COPY requirements.txt .
RUN uv pip install --system --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R celeryuser:celeryuser /app
USER celeryuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]