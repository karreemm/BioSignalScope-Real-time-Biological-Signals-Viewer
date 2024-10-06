import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
from classes.viewer import Viewer
from classes.channel_ import CustomSignal

class TestWindow(QMainWindow):
    def __init__(self, signal):
        super().__init__()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        
        self.plot_widget = Viewer()
        self.layout.addWidget(self.plot_widget)
        if signal:
            self.plot_widget.add_channel(signal)


def main():
    app = QApplication(sys.argv)
    data = pd.read_csv('100.csv')
    data = data['MLII']
    signal = CustomSignal(data)
    window = TestWindow(signal)
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
