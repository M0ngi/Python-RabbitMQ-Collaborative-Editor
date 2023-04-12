import pika
from pika.exchange_type import ExchangeType
from Config import Config
import threading


class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(Config.RMQ_CONNECTION)
        self.channel = self.connection.channel()
        # __init__
    
    def declareAndBindQueueExchange(self, queue, exchange):
        self.declareQueue(queue=queue)
        self.declareExchange(exchange=exchange, exchType=ExchangeType.fanout)
        self.channel.queue_bind(exchange=exchange, queue=queue)
        # declareAndBindQueueExchange

    def declareQueue(self, queue, **args):
        res = self.channel.queue_declare(queue=queue, durable=True, **args)
        return res.method.queue
        
    def declareExchange(self, exchange, exchType):
        return self.channel.exchange_declare(exchange=exchange, exchange_type=exchType)
    
    def bindQueueExch(self, queue, exchange):
        return self.channel.queue_bind(exchange=exchange, queue=queue)
    
    def sendMessage(self, message, queue="", exchange=""):
        return self.channel.basic_publish(exchange=exchange,
                      routing_key=queue,
                      body=message)
    
    def readQueue(self, queue, **args):
        return self.channel.basic_get(queue, **args)

    def sendNack(self, tag):
        self.channel.basic_nack(tag)
    
    def sendAck(self, tag):
        self.channel.basic_ack(tag)
