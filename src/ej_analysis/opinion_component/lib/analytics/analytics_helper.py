from . import analytics_api as analytics
import datetime


class AnalyticsClient:
    def __init__(self):
        self.analytics_api_client = analytics.initialize_analyticsreporting()

    def get_report_total_value(self, reports):
        report = reports.get("reports")[0]
        if report:
            new_users = report.get("data").get("totals")[0].get("values")[0]
            return int(new_users)

    def get_report(self, startDate, endDate, viewId, utm_medium, utm_campaign, utm_source):
        return (
            self.analytics_api_client.reports()
            .batchGet(
                body={
                    "reportRequests": [
                        {
                            "viewId": viewId,
                            "dateRanges": {
                                "startDate": startDate.strftime("%Y-%m-%d"),
                                "endDate": endDate.strftime("%Y-%m-%d"),
                            },
                            "metrics": [
                                {"expression": "ga:users", "alias": "users", "formattingType": "INTEGER"}
                            ],
                            "dimensions": [
                                {"name": "ga:pagePath"},
                                {"name": "ga:campaign"},
                                {"name": "ga:medium"},
                                {"name": "ga:source"},
                            ],
                            "filtersExpression": self.get_filter_expression(
                                utm_medium, utm_campaign, utm_source
                            ),
                        }
                    ],
                    "useResourceQuotas": False,
                }
            )
            .execute()
        )

    def get_filter_expression(self, utm_medium, utm_campaign, utm_source):
        if utm_source == "None" and utm_medium == "None" and utm_campaign == "None":
            return ""
        return f"ga:campaign=={utm_campaign},ga:source=={utm_source},ga:medium=={utm_medium}"
