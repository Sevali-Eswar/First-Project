import socket
from time import sleep
from json import dumps
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError

# Establish socket connection to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(('servers', 12345))
server.settimeout(10)

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    api_version=(0, 11, 5),
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

# Function to send message to Kafka topic
def send_message(message):
    while True:
        try:
            producer.send('device_data', message)
            return
        except KafkaTimeoutError:
            print("Failed to send message, retrying in 5 seconds...")
            sleep(5)

# Receive messages from socket and send to Kafka
while True:
    try:
        message = server.recv(1024).decode('utf-8')
        send_message(message)
    except socket.timeout:
        print("No messages received in the last 10 seconds.")
    except ConnectionResetError:
        print("Connection reset by peer.")
        break

server.close()
