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

    def get_dags(self):
        response = requests.get(
            f"{self.client_variables['API_HOST']}/api/v1/dags/ej_analysis_dag/dagRuns",
            auth=(self.client_variables["AIRFLOW_USERNAME"], self.client_variables["AIRFLOW_PASSWORD"]),
        )
        return response.json()

    def lattest_dag_is_running(self):
        dags = self.get_dags()
        dag_runs = dags.get("dag_runs")
        conversation_dag_runs = list(
            filter(lambda dag: dag.get("conf").get("conversation_id") == self.conversation_id, dag_runs)
        )
        return conversation_dag_runs[len(conversation_dag_runs) - 1].get("state") == "running"

    def get_airflow_connection_variables(self):
        return {
            "API_HOST": os.getenv("AIRFLOW_HOST", "http://localhost:8080"),
            "AIRFLOW_USERNAME": os.getenv("AIRFLOW_USERNAME", "airflow"),
            "AIRFLOW_PASSWORD": os.getenv("AIRFLOW_PASSWORD", "airflow"),
        }
