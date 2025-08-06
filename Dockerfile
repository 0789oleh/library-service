FROM python:3.10

# Create a non-root user with home directory
RUN useradd -m -u 1000 -s /bin/bash celeryuser
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Set ownership to celeryuser
RUN chown -R celeryuser:celeryuser /app
USER celeryuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]