# import pymango
from pymongo import MongoClient
conn = MongoClient("mongodb+srv://eswar:541%40ramyA@cluster0.m5atrih.mongodb.net/test")
# conn = MongoClient("mongodb://localhost:27017/")
db = conn['database']
coll = db['users']
coll1 = db['shipment']
coll2 = db['device_data']

