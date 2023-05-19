# import pymango
from pymongo import MongoClient
conn = MongoClient("mongodb+srv://eswar:541%40ramyA@cluster0.m5atrih.mongodb.net/test")
# conn = MongoClient("mongodb://localhost:27017/")
database= conn['SCMX']
collection = database['user_details']
collection1 = database['shipment']
collection2 = database['device_data']

