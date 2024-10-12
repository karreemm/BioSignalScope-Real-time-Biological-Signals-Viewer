import sys
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))  
        self.y = [0] * 100 

        self.data_line = self.graphWidget.plot(self.x, self.y)

        self.timer = QTimer()
        self.timer.setInterval(500) 
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
        data = response.json()
        price = float(data['bpi']['USD']['rate'].replace(',', ''))

        self.y = self.y[1:]
        self.y.append(price)  

        self.data_line.setData(self.x, self.y)  

app = QtWidgets.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
