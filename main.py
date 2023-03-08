from MainWindow import Ui_MainWindow
from PyQt5 import QtWidgets
from RMQConnection import RabbitMQConnection


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    conn = RabbitMQConnection()

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(conn)
    ui.setupUi(MainWindow)
    MainWindow.show()
    
    sys.exit(app.exec_())

