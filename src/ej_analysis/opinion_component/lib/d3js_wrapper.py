from django.utils.translation import ugettext_lazy as _


class D3jsWrapper:
    def __init__(self, aquisition, engajement):
        self.aquisition = aquisition
        self.engagement = engajement

    def get_data(self):
        return {
            "name": "engagement",
            "value": self.engagement,
            "label": _("Engagement"),
            "children": [
                {"name": "aquisition", "label": _("Aquisition"), "value": self.aquisition, "children": []}
            ],
        }
