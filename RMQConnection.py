import pika
from pika.exchange_type import ExchangeType
from Config import Config
from RMQConsumer import RabbitMQConsumer
from RMQPublisher import RabbitMQPublisher
import uuid


class RabbitMQConnection:
    def __init__(self):
        self.clientId = str(uuid.uuid4())
        self.consumer = RabbitMQConsumer()
        self.publisher = RabbitMQPublisher()
        # __init__
    
    def startConsumer(self):
        self.consumer.start()
    