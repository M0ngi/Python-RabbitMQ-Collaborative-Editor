from PyQt5 import QtCore, QtGui, QtWidgets
import pika, json
import threading
from RMQConnection import RabbitMQConnection


class ParagraphTextEdit(QtWidgets.QTextEdit):
    OFFSET = 140
    updateValue = QtCore.pyqtSignal(str)

    def __init__(self, panelContext: QtWidgets.QWidget, connection: RabbitMQConnection, index: int):
        super(ParagraphTextEdit, self).__init__(panelContext)
        self.index = index
        self.connection = connection
        self.identifier = f"inputBox{self.index}"
        self.exchange = f"exchange.{self.identifier}"
        self.updateQueue = f"{self.connection.clientId}.{self.identifier}"
        self.lastUpdatedValue = ""
        
        self.setGeometry(QtCore.QRect(170, 20 + index*ParagraphTextEdit.OFFSET, 431, 121)) # 
        self.setObjectName(self.identifier)
        self.updateValue.connect(self.setText)
        
        # Used for locks
        self.connection.publisher.declareQueue(self.identifier, arguments={'x-max-length': 1})
        # self.connection.consumer.listenQueue(self.identifier, self.lockManager)

        # Used for message updates
        self.connection.publisher.declareAndBindQueueExchange(self.updateQueue, self.exchange)
        self.connection.consumer.listenQueue(self.updateQueue, self.onMessageUpdate)
        # __init__

    def lockManager(self, ch, method, properties, body):
        # WIP
        print(body)

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
        self.connection.publisher.sendMessage(queue=self.identifier, message=json.dumps(payload))
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
        
        payload = {
            "message": self.toPlainText(),
            "index": self.index
        }
        self.connection.publisher.sendMessage(exchange=self.exchange, message=json.dumps(payload))
        self.lastUpdatedValue = self.toPlainText()
        # focusOutEvent
    

