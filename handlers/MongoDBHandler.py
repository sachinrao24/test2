from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

class MongoDBHandler():
    def __init__(self, collection_name):
        MONGODB_URI = os.environ.get("MONGODB_URI")
        MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")

        self.client = MongoClient(MONGODB_URI, server_api=ServerApi('1'))

        self.db = self.client[MONGODB_DATABASE]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        self.collection.insert_many(data)

    def read_data(self, query=None):
        # collection.find() returns a cursor object that needs to be iterated through to get documents
        if query:
            data = self.collection.find(query)
        else:
            data = self.collection.find()
        data_list = list(data)
        return data_list
    
    def update_data(self, query, data):
        update_query = {"$set": data}
        self.collection.update_one(query, update_query)

    def delete_data(self, data):
        self.collection.delete_one(data)
    
    def close_connection(self):
        self.client.close()