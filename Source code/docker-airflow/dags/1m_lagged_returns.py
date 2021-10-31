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
        'retry_delay'           : timedelta(seconds=1),
        'image'                 : 'workflow_1d:v4',
        #'docker_conn_id'        : "docker_snaps_conn_id",
        'auto_remove'           : True,
        'api_version'           : 'auto',
        #'network_mode'          : 'bridge',
        #'queue'                 : "HEL1DC2-tuimprt",
        'docker_url'            : 'unix://var/run/docker.sock',
        #'user'                  : 'tuimprt'
}


with DAG('workflow_1d_v2', default_args=default_args, schedule_interval="* * * * *", catchup=False) as dag:

        t1 = DockerOperator(
            task_id='initialize_and_run',
            image='workflow_1d:v4'
        )

        t1

