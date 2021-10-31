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
        'retries'               : 2,
        'retry_delay'           : timedelta(minutes=1),
        'image'                 : 'test_print',
        #'docker_conn_id'        : "docker_snaps_conn_id",
        'auto_remove'           : True,
        'api_version'           : 'auto',
        #'network_mode'          : 'bridge',
        'volumes'               : ['/home/szymi/TestTask/pipipizza/data:/app/data', '/var/run/:/var/run:rw'],
        #'queue'                 : "HEL1DC2-tuimprt",
        'docker_url'            : 'unix://var/run/docker.sock',
        #'user'                  : 'tuimprt'
}


with DAG('test-dag', default_args=default_args, schedule_interval="* * * * *", catchup=False) as dag:

        

        t2 = BashOperator(
            task_id = 'docker_images',
            bash_command='docker exec -t test python test-runner.py t1'
        )



