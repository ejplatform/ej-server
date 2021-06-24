from .analytics.analytics_helper import AnalyticsClient
from django.utils.translation import ugettext_lazy as _


class AquisitionService:
    def __init__(self, start_date, end_date, view_id, votes):
        self.start_date = start_date
        self.end_date = end_date
        self.view_id = view_id
        self.votes = list(votes)

    def count_engajement(self):
        analytics_client = AnalyticsClient()
        report = analytics_client.get_report(self.start_date, self.end_date, self.view_id)
        return analytics_client.get_report_total_value(report)

    def count_aquisition(self):
        page_aquisition = []
        for vote in self.votes:
            metadata = vote.author.metadata_set.first()
            if metadata:
                page_aquisition.append(metadata)
        return len(page_aquisition)

    def d3js_data(self):
        page_engagement = self.count_engajement()
        page_aquisition = self.count_aquisition()
        return {
            "name": "engagement",
            "value": page_engagement,
            "label": _("Engagement"),
            "children": [
                {"name": "aquisition", "label": _("Aquisition"), "value": page_aquisition, "children": []}
            ],
        }
