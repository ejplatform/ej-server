from pymongo import MongoClient


class MongodbWrapper:
    def __init__(
        self,
        conversation_id,
        start_date=None,
        end_date=None,
        utm_medium=False,
        utm_campaign=False,
        utm_source=False,
    ):
        client = MongoClient("192.168.15.101", 27017, username="mongo", password="mongo")
        self.db = client.admin.conversations
        self.start_date = start_date
        self.end_date = end_date
        self.utm_medium = utm_medium
        self.utm_campaign = utm_campaign
        self.utm_source = utm_source
        self.conversation_id = conversation_id

    def get_page_aquisition(self):
        if self.utm_source == "None" and self.utm_medium == "None" and self.utm_campaign == "None":
            return len(self.db.distinct("author"))
        return len(
            self.db.find(
                {
                    "$or": [
                        {"analytics_source": self.utm_source},
                        {"analytics_campaign": self.utm_campaign},
                        {"analytics_medium": self.utm_medium},
                    ]
                }
            ).distinct("author")
        )

    def get_utm_sources(self):
        return self.db.distinct("analytics_source")

    def get_utm_campaigns(self):
        return self.db.distinct("analytics_campaign")

    def get_utm_medium(self):
        return self.db.distinct("analytics_medium")

    def conversation_data_exists(self):
        return self.db.find_one({"conversation_id": int(self.conversation_id)})
