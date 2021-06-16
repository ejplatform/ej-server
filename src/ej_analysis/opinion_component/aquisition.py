from .analytics.analytics_helper import AnalyticsClient
from django.utils.translation import ugettext_lazy as _


class AnalyticsHelper:
    def __init__(self, start_date, end_date, view_id):
        self.start_date = start_date
        self.end_date = end_date
        self.view_id = view_id

    def get_page_engajement(self):
        analytics_client = AnalyticsClient()
        report = analytics_client.get_report(self.start_date, self.end_date, self.view_id)
        return analytics_client.get_report_total_value(report)
