# import pymango
from pymongo import MongoClient
conn = MongoClient("mongodb+srv://eswar:541%40ramyA@cluster0.m5atrih.mongodb.net/test")
# conn = MongoClient("mongodb://localhost:27017/")
db = conn['SCMX']
collection = db['user_details']
collection1 = db['shipment']
collection2 = db['device_data']

