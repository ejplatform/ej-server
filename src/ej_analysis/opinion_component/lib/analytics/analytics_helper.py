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

    def get_report(self, startDate, endDate, viewId):
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
                            "dimensions": [{"name": "ga:pagePath"}],
                        }
                    ],
                    "useResourceQuotas": False,
                }
            )
            .execute()
        )
