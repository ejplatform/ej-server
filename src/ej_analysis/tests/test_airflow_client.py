import pytest
import mock
from ej_analysis.airflow_client import AirflowClient

RUNNING_DAG_RUNS = {
    "dag_runs": [
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T15:56:29.172548+00:00",
            "end_date": "2021-07-07T15:56:38.092796+00:00",
            "execution_date": "2021-07-07T15:56:29.172548+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T15:56:29.177961+00:00",
            "state": "success",
        },
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T16:12:28.300388+00:00",
            "end_date": "2021-07-07T16:12:39.108154+00:00",
            "execution_date": "2021-07-07T16:12:28.300388+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T16:12:28.304063+00:00",
            "state": "success",
        },
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T16:24:17.448517+00:00",
            "end_date": "2021-07-07T16:24:25.060546+00:00",
            "execution_date": "2021-07-07T16:24:17.448517+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T16:24:17.451463+00:00",
            "state": "running",
        },
    ],
    "total_entries": 3,
}

SUCESS_DAG_RUNS = {
    "dag_runs": [
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T15:56:29.172548+00:00",
            "end_date": "2021-07-07T15:56:38.092796+00:00",
            "execution_date": "2021-07-07T15:56:29.172548+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T15:56:29.177961+00:00",
            "state": "success",
        },
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T16:12:28.300388+00:00",
            "end_date": "2021-07-07T16:12:39.108154+00:00",
            "execution_date": "2021-07-07T16:12:28.300388+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T16:12:28.304063+00:00",
            "state": "success",
        },
        {
            "conf": {
                "analytics_view_id": "246115891",
                "conversation_end_date": "",
                "conversation_id": 66,
                "conversation_start_date": "",
            },
            "dag_id": "ej_analysis_dag",
            "dag_run_id": "manual__2021-07-07T16:24:17.448517+00:00",
            "end_date": "2021-07-07T16:24:25.060546+00:00",
            "execution_date": "2021-07-07T16:24:17.448517+00:00",
            "external_trigger": True,
            "start_date": "2021-07-07T16:24:17.451463+00:00",
            "state": "success",
        },
    ],
    "total_entries": 3,
}


class TestAirflowClient:
    def test_get_dag_running_status(self):
        airflow_client = AirflowClient(66, 123456)
        airflow_client.get_dags = mock.MagicMock(return_value=RUNNING_DAG_RUNS)
        is_runing = airflow_client.lattest_dag_is_running()
        assert is_runing

    def test_get_dag_sucess_status(self):
        airflow_client = AirflowClient(66, 123456)
        airflow_client.get_dags = mock.MagicMock(return_value=SUCESS_DAG_RUNS)
        is_runing = airflow_client.lattest_dag_is_running()
        assert not is_runing

    def test_conversation_without_dag(self):
        airflow_client = AirflowClient(90, 123456)
        airflow_client.get_dags = mock.MagicMock(return_value=SUCESS_DAG_RUNS)
        is_runing = airflow_client.lattest_dag_is_running()
        assert not is_runing

    def test_get_dag_payload(self):
        airflow_client = AirflowClient(90, 123456)
        assert airflow_client.get_dag_payload().get("conf") == {
            "conversation_start_date": "",
            "conversation_end_date": "",
            "conversation_id": 90,
            "analytics_view_id": 123456,
        }
