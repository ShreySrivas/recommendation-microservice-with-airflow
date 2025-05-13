FROM python:3.10-slim

# 1) Install OS-level build dependencies for LightFM
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      gfortran \
      libopenblas-dev \
      liblapack-dev \
      libomp-dev \
      python3-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy training script
COPY train.py .

# 4) Default command
CMD ["python", "train.py"]
