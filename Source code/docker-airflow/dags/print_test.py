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


with DAG('print_test', default_args=default_args, schedule_interval="*/5 * * * *", catchup=False) as dag:

        

        t1 = BashOperator(
            task_id = 'indicators_creation',
            bash_command="docker exec -t print_container python run.py {{ ts }}"
        )
        
        t1



