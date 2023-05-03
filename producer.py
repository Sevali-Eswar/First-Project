import socket
from time import sleep
from json import dumps
from kafka import KafkaProducer

# Establish socket connection to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((socket.gethostname(), 5050))
message = server.recv(1024).decode('utf-8')
server.close()

# Send message to Kafka topic
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))
producer.send('device-data', message)
producer.close()

# Wait for 5 seconds
sleep(5)
