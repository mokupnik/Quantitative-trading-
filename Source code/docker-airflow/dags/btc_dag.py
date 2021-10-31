from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.operators.docker_operator import DockerOperator
import datetime
from airflow.utils.dates import days_ago

default_args = {
        'depend_on_past'        : False,
        'start_date'            : datetime.datetime(2021,1,18),
        'email_on_failure'      : False,
        'email_on_retry'        : False,
        'retries'               : 0,
        'retry_delay'           : timedelta(minutes=1),
        'auto_remove'           : True,
        'api_version'           : 'auto',
        'volumes'               : ['/home/szymi/TestTask/pipipizza/data:/app/data', '/var/run/:/var/run:rw'],
        'docker_url'            : 'unix://var/run/docker.sock'
}


with DAG(
    'btc_dag_v1', 
    default_args=default_args, 
    schedule_interval="*/5 * * * *", 
    catchup=False
) as dag:
    
        t1 = BashOperator(
            task_id = 'indicators_creation',
            bash_command=\
            "docker exec -t btc_5m_dag python create_indicators.py {{ ts }}"
        )
        
        t2 = BashOperator(
            task_id = 'predictor',
            bash_command="\
            docker exec -t btc_5m_dag python make_prediction.py {{ ts }}"
        )
        
        t3 = BashOperator(
            task_id = 'trader',
            bash_command=\
            "docker exec -t alpha_trader python Trader_runner.py {{ ts }}",
            trigger_rule='all_done')
        
        t1>>t2>>t3



