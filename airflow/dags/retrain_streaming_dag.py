from airflow import DAG
from airflow.operators.bash import BashOperator
import pendulum

DEFAULT_ARGS = {
    "owner": "recsys",
    "depends_on_past": False,
    "retries": 1,
}

DOCKER_NETWORK = "recsys_recsys_default"

with DAG(
    "retrain_and_stream",
    schedule_interval="*/5 * * * *",
    start_date=pendulum.datetime(2025, 5, 1, tz="UTC"),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["recsys", "streaming"],
) as dag:

    stream = BashOperator(
        task_id="stream_data",
        cwd="/opt/recsys",   # <- run from project root
        bash_command="docker compose run --rm stream"
    )

    retrain = BashOperator(
        task_id="retrain_model",
        cwd="/opt/recsys",   # <- same
        bash_command=(
            "docker run --rm "
            f"--network {DOCKER_NETWORK} "
            "-e DATABASE_URL=${DATABASE_URL} "
            "recsys_trainer:latest "
            "python training/train.py"
        )
    )

    stream >> retrain
