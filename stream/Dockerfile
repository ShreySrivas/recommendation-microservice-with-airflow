FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the stream simulator
COPY simulate_stream.py .

# Default command: run one batch of streaming
CMD ["python", "simulate_stream.py"]
