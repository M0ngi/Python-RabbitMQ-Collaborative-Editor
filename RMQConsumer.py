import pika
from pika.exchange_type import ExchangeType
from Config import Config
import threading


class RabbitMQConsumer(threading.Thread):
    def __init__(self):
        super(RabbitMQConsumer, self).__init__()

        self.connection = pika.BlockingConnection(Config.RMQ_CONNECTION)
        self.channel = self.connection.channel()
        # __init__
    
    def run(self):
        threading.Thread(target=self.channel.start_consuming, daemon=True).start()
    
    def updateListener(self, ch, method, properties, body):
        print(ch, method, properties, body)
    
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
    
    def sendAck(self, tag):
        self.channel.basic_ack(tag)

    def listenQueue(self, queue, onmessage, **args):
        return self.channel.basic_consume(queue=queue, on_message_callback=onmessage, **args)

    def cancelListener(self, tag):
        self.channel.basic_cancel(tag)
