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
        return self.count_total_users_from_reports(report)

    def get_report(self):
        body = {
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
                    "filtersExpression": self.get_filter_expression()
                }
            ],
            "useResourceQuotas": False,
        }
        return self.analytics_client.reports().batchGet(body=body).execute()

    def get_filter_expression(self):
        if self.utm_source == "None" and self.utm_medium == "None" and self.utm_campaign == "None":
            return ""
        return f"ga:campaign=={self.utm_campaign},ga:source=={self.utm_source},ga:medium=={self.utm_medium}"

    def count_total_users_from_reports(self, reports):
        report = reports.get("reports")[0]
        if report:
            new_users = report.get("data").get("totals")[0].get("values")[0]
            return int(new_users)
