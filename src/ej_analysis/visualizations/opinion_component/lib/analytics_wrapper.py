from .analytics import analytics_api as analytics


class AnalyticsWrapper:
    def __init__(self, start_date, end_date, view_id, utm_medium, utm_campaign, utm_source):
        self.start_date = start_date
        self.end_date = end_date
        self.view_id = view_id
        self.utm_medium = utm_medium
        self.utm_campaign = utm_campaign
        self.utm_source = utm_source

    def get_page_engajement(self):
        self.analytics_client = analytics.initialize_analyticsreporting()
        report = self.get_report()
        return self.count_report_users(report)

    def get_report(self):
        body = self._get_report_body()
        return self.analytics_client.reports().batchGet(body=body).execute()

    def _get_report_body(self):
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": [
                        {
                            "startDate": self.start_date.strftime("%Y-%m-%d"),
                            "endDate": self.end_date.strftime("%Y-%m-%d"),
                        }
                    ],
                    "metrics": [{"expression": "ga:users", "alias": "users", "formattingType": "INTEGER"}],
                    "dimensions": [
                        {"name": "ga:pagePath"},
                        {"name": "ga:campaign"},
                        {"name": "ga:medium"},
                        {"name": "ga:source"},
                    ],
                    "filtersExpression": self.get_filter_expression(),
                }
            ],
            "useResourceQuotas": False,
        }

    def get_filter_expression(self):
        if (
            self.utm_is_valid(self.utm_source)
            and self.utm_is_valid(self.utm_medium)
            and self.utm_is_valid(self.utm_campaign)
        ):
            return f"ga:campaign=={self.utm_campaign},ga:source=={self.utm_source},ga:medium=={self.utm_medium}"
        return ""

    def count_report_users(self, reports):
        report = reports.get("reports")[0]
        if report:
            new_users = report.get("data").get("totals")[0].get("values")[0]
            return int(new_users)

    def utm_is_valid(self, utm_value):
        return utm_value != "None" and utm_value != ""
