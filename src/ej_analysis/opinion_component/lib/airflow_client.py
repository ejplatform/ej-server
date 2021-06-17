import requests


class AirflowClient:
    def __init__(self, conversation_id):
        self.conversation_id = conversation_id

    def trigger_dag(self):
        requests.post(
            "http://192.168.15.101:8080/api/v1/dags/ej_analysis_dag/dagRuns",
            json={
                "conf": {
                    "conversation_start_date": "2020-10-01",
                    "conversation_end_date": "2021-04-01",
                    "conversation_id": self.conversation_id,
                }
            },
            auth=("airflow", "airflow"),
        )
