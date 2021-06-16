from pymongo import MongoClient
class MongodbWrapper():

    def __init__(self):
        client = MongoClient("192.168.15.101", 27017, username="mongo", password="mongo")
        self.conversations = client.admin.conversations

    def get_page_aquisition(self):
        return len(self.conversations.distinct('author'))
