import pika


class Config:
    HOST = "localhost"
    RMQ_CONNECTION = pika.ConnectionParameters(HOST, heartbeat=0)

