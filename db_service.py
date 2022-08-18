from tinydb import TinyDB, Query


class DbService:
    def __init__(self):
        self.dbname = 'tweets.json'

    def initConnect(self):
        self.db = TinyDB(self.dbname)

    def insert(self, data):
        self.db.insert(data)

    def fetch(self):
        return self.db.all()

    def removeAll(self):
        self.db.truncate()


# db = DbService()
# db.initConnect()
# print(db.fetch())
# db.removeAll()
# print(db.fetch())