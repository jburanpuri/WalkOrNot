# database.py
from pymongo import MongoClient
import os
from datetime import datetime


class Database:
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        self.db = client["walkornot"]
        self.collection = self.db["history"]

    def get_previous_requests(self):
        return list(self.collection.find({}, {"_id": 0, "time": 1, "city": 1, "temperature": 1}).sort("time", -1))

    def save_request_to_db(self, city, temperature):
        current_time = datetime.now()
        request_data = {
            "time": current_time,
            "city": city,
            "temperature": temperature,
        }
        self.collection.insert_one(request_data)
