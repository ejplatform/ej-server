import os
import requests


class AirflowClient:
    def __init__(self, conversation_id, analytics_view_id):
        self.conversation_id = conversation_id
        self.analytics_view_id = analytics_view_id
        self.client_variables = self.get_airflow_connection_variables()

    def trigger_dag(self):
        requests.post(
            f"{self.client_variables['API_HOST']}/api/v1/dags/ej_analysis_dag/dagRuns",
            json={
                "conf": {
                    "conversation_start_date": "2020-10-01",
                    "conversation_end_date": "2021-04-01",
                    "conversation_id": self.conversation_id,
                    "analytics_view_id": self.analytics_view_id,
                }
            },
            auth=(self.client_variables["AIRFLOW_USERNAME"], self.client_variables["AIRFLOW_PASSWORD"]),
        )

    def get_airflow_connection_variables(self):
        return {
            "API_HOST": os.getenv("AIRFLOW_HOST", "http://localhost:8080"),
            "AIRFLOW_USERNAME": os.getenv("AIRFLOW_USERNAME", "airflow"),
            "AIRFLOW_PASSWORD": os.getenv("AIRFLOW_PASSWORD", "airflow"),
        }
