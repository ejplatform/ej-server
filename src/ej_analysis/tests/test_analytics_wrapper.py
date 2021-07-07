import pytest
import mock
import datetime
from ej_analysis.visualizations.opinion_component.lib.analytics_wrapper import AnalyticsWrapper


class TestAnalyticsWrapper:
    def test_get_report_body_with_emtpy_utms(self):
        start_date = datetime.date(2021, 7, 1)
        end_date = datetime.date(2021, 7, 7)
        analytics_wrapper = AnalyticsWrapper(start_date, end_date, 123456, "", "", "")
        report_body = analytics_wrapper._get_report_body()
        assert report_body == {
            "reportRequests": [
                {
                    "viewId": 123456,
                    "dateRanges": [
                        {
                            "startDate": start_date.strftime("%Y-%m-%d"),
                            "endDate": end_date.strftime("%Y-%m-%d"),
                        }
                    ],
                    "metrics": [{"expression": "ga:users", "alias": "users", "formattingType": "INTEGER"}],
                    "dimensions": [
                        {"name": "ga:pagePath"},
                        {"name": "ga:campaign"},
                        {"name": "ga:medium"},
                        {"name": "ga:source"},
                    ],
                    "filtersExpression": "",
                }
            ],
            "useResourceQuotas": False,
        }

    def test_get_report_body_with_valid_utms(self):
        start_date = datetime.date(2021, 7, 1)
        end_date = datetime.date(2021, 7, 7)
        utm_medium = "fase3"
        utm_campaign = "vacina"
        utm_source = "direct"
        analytics_wrapper = AnalyticsWrapper(
            start_date, end_date, 123456, utm_medium, utm_campaign, utm_source
        )
        report_body = analytics_wrapper._get_report_body()
        assert report_body == {
            "reportRequests": [
                {
                    "viewId": 123456,
                    "dateRanges": [
                        {
                            "startDate": start_date.strftime("%Y-%m-%d"),
                            "endDate": end_date.strftime("%Y-%m-%d"),
                        }
                    ],
                    "metrics": [{"expression": "ga:users", "alias": "users", "formattingType": "INTEGER"}],
                    "dimensions": [
                        {"name": "ga:pagePath"},
                        {"name": "ga:campaign"},
                        {"name": "ga:medium"},
                        {"name": "ga:source"},
                    ],
                    "filtersExpression": f"ga:campaign=={utm_campaign},ga:source=={utm_source},ga:medium=={utm_medium}",
                }
            ],
            "useResourceQuotas": False,
        }
