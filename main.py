import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
from classes.viewer import Viewer
from classes.channel_ import CustomSignal

class TestWindow(QMainWindow):
    def __init__(self, signals):
        super().__init__()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)
        self.play_button = QPushButton("play")
        self.stop_button = QPushButton("stop")
        
        
        self.plot_widget = Viewer()
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.stop_button)
        
        self.play_button.clicked.connect(self.plot_widget.play)
        self.stop_button.clicked.connect(self.plot_widget.pause)
        if signals:
            for signal in signals:
                self.plot_widget.add_channel(signal)
            self.plot_widget.play()

def main():
    app = QApplication(sys.argv)
    data = pd.read_csv('100.csv')
    data1 = data['MLII']
    data2 = data['V5']
    signal = CustomSignal(data1)
    signal2 = CustomSignal(data2)
    window = TestWindow([signal, signal2])
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()
