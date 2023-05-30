# import pymango
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongouri=os.getenv("mongouri")

conn =  MongoClient(mongouri)
# conn = MongoClient("mongodb://localhost:27017/")
database= conn['SCMX']
collection = database['user_details']
collection1 = database['shipment']
collection2 = database['device_data']

