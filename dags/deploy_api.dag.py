from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'deploy_api',
    description='Déploiement FastAPI depuis GitHub',
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['deploy', 'api']
)

pull_code = BashOperator(
    task_id='pull_github',
    bash_command="""
        cd /opt/airflow
        rm -rf MLops_vehicule_price
        git clone https://github.com/sloffer47/MLops_vehicule_price.git
    """,
    dag=dag
)

build_image = BashOperator(
    task_id='build_docker',
    bash_command="""
        cd /opt/airflow/MLops_vehicule_price
        docker build -t vehicule-price-api:latest .
    """,
    dag=dag
)

stop_old = BashOperator(
    task_id='stop_old_container',
    bash_command='docker stop vehicule_price_api || true',
    dag=dag
)

remove_old = BashOperator(
    task_id='remove_old_container',
    bash_command='docker rm vehicule_price_api || true',
    dag=dag
)

start_new = BashOperator(
    task_id='start_new_container',
    bash_command="""
        docker run -d \
            --name vehicule_price_api \
            -p 7777:7777 \
            -v /opt/airflow/models:/app/models \
            -v /opt/airflow/data:/app/data \
            --restart unless-stopped \
            vehicule-price-api:latest
    """,
    dag=dag
)

health_check = BashOperator(
    task_id='health_check',
    bash_command='sleep 5 && curl -f http://localhost:7777/health || exit 1',
    dag=dag
)

pull_code >> build_image >> stop_old >> remove_old >> start_new >> health_check
