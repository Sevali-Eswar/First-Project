from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads
import json

conn = MongoClient("mongodb+srv://eswar:541%40ramyA@cluster0.m5atrih.mongodb.net/test")
db = conn['database']
coll2 = db['device-data']

consumer = KafkaConsumer(
    'device-data',
     bootstrap_servers=['localhost:9092'],
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

for message in consumer:
    try:
        data = json.loads(message.value)
        coll2.insert_one(data)
        print(f"{data} added to {coll2}")
    except Exception as e:
        print(f"Error: {e}")


