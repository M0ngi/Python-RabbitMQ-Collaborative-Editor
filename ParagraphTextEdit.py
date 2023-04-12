from PyQt5 import QtCore, QtGui, QtWidgets
import pika, json
import threading, time
from RMQConnection import RabbitMQConnection


class ParagraphTextEdit(QtWidgets.QTextEdit):
    OFFSET = 90
    updateValue = QtCore.pyqtSignal(str)

    def __init__(self, panelContext: QtWidgets.QWidget, connection: RabbitMQConnection, index: int):
        super(ParagraphTextEdit, self).__init__(panelContext)
        self.index = index
        self.connection = connection
        self.identifier = f"inputBox{self.index}"
        self.exchange = f"exchange.{self.identifier}"
        self.updateQueue = f"{self.connection.clientId}.{self.identifier}"
        self.lastUpdatedValue = ""

        print("ID: "+self.connection.clientId)
        
        self.setGeometry(QtCore.QRect(170, 20 + index*ParagraphTextEdit.OFFSET, 431, 70)) # 
        self.setObjectName(self.identifier)
        self.updateValue.connect(self.setText)
        
        # Used for locks
        self.connection.publisher.declareQueue(self.identifier, arguments={'x-max-length': 1, "x-overflow":"reject-publish"})

        # Used for message updates
        self.connection.publisher.declareAndBindQueueExchange(self.updateQueue, self.exchange)
        self.connection.consumer.listenQueue(self.updateQueue, self.onMessageUpdate)
        # __init__

    def onMessageUpdate(self, ch, method, properties, body):
        delivery_tag = method.delivery_tag
        payload = json.loads(body)
        if 'index' not in payload or 'message' not in payload:
            return
        if payload['index'] != self.index:
            return
        
        self.clearFocus()
        self.updateValue.emit(payload['message'])
        self.connection.consumer.sendAck(delivery_tag)

    def requestEditLock(self):
        payload = {
            "user": self.connection.clientId
        }
        try:
            self.connection.publisher.sendMessage(queue=self.identifier, message=json.dumps(payload))
        except Exception as e:
            pass
        
        body = None
        try:
            method, properties, body = self.connection.publisher.readQueue(self.identifier, auto_ack=False)
            self.connection.publisher.sendNack(method.delivery_tag)
            print(body)
        except Exception as e:
            print("Error" + "-"*50)
            print(e)
            pass

        if body is None:
            return
        
        body = json.loads(body)
        print(body)
        if "user" not in body:
            self.clearFocus()
            return
        
        if body["user"] != self.connection.clientId:
            self.clearFocus()
            return
        # requestEditLock
    
    def focusInEvent(self, e):
        super(ParagraphTextEdit, self).focusInEvent(e)
        print("focus on "+str(self.index))
        
        self.requestEditLock()
        # focusInEvent
    
    def focusOutEvent(self, e):
        super(ParagraphTextEdit, self).focusOutEvent(e)
        if self.lastUpdatedValue == self.toPlainText():
            return
        print("focus out "+str(self.index))
        
        try:
            method, properties, body = self.connection.publisher.readQueue(self.identifier, auto_ack=False)
            self.connection.publisher.sendAck(method.delivery_tag)
        except Exception as e:
            print("Error" + "-"*50)
            print(e)
            pass
        
        payload = {
            "message": self.toPlainText(),
            "index": self.index
        }
        self.connection.publisher.sendMessage(exchange=self.exchange, message=json.dumps(payload))
        self.lastUpdatedValue = self.toPlainText()
        # focusOutEvent
    

