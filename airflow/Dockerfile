FROM apache/airflow:2.5.1-python3.10

USER root

# 1) Install Docker CLI and docker-compose from APT
RUN apt-get update \
    && apt-get install -y docker.io docker-compose \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy requirements for later
COPY requirements.txt /requirements.txt

# 3) Switch to airflow user for Python installs
USER airflow

# 4) Install Python deps (Airflow providers, psycopg, pandas, etc.)
#    and docker-compose via pip into ~/.local
RUN pip install --user --upgrade pip \
    && pip install --user --no-cache-dir -r /requirements.txt

# 5) Add the user-local bin to PATH so airflow and CLI tools are found
ENV PATH="${PATH}:/home/airflow/.local/bin"

# 6) Back to root to copy DAGs
USER root
COPY dags/ /opt/airflow/dags/
RUN chown -R airflow: /opt/airflow/dags

# 7) Finally switch back to airflow
USER airflow

# 8) Launch Airflow in standalone mode
CMD ["airflow", "standalone"]
