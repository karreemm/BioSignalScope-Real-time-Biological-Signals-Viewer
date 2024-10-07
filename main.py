import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSlider, QScrollBar
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
        self.current_x_axis_start_value = 0
        self.current_y_axis_start_value = 0
        ## slider feature
        self.cine_scrollbar = QSlider()
        self.cine_scrollbar.setMaximum(300)
        self.cine_scrollbar.setMinimum(1)
        
        self.plot_widget = Viewer()
        self.viewBox = self.plot_widget.getViewBox()
        self.layout.addWidget(self.plot_widget)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.stop_button)
        # cine slider feature 
        self.layout.addWidget(self.cine_scrollbar)
        # scrolling_x_axis slider feature
        self.scrolling_x_axis_scrollbar = QScrollBar()
        # self.scrolling_x_axis_scrollbar.setMinimum(0)
        self.scrolling_x_axis_scrollbar.setMinimumHeight(100)
        self.layout.addWidget(self.scrolling_x_axis_scrollbar)
        
        # scrolling_y_axis slider feature
        self.scrolling_y_axis_scrollbar = QScrollBar()
        self.scrolling_y_axis_scrollbar.setMinimumHeight(100)
        self.layout.addWidget(self.scrolling_y_axis_scrollbar)
        
        self.play_button.clicked.connect(self.plot_widget.play)
        self.stop_button.clicked.connect(self.plot_widget.pause)
        
        if signals:
            for signal in signals:
                self.plot_widget.add_channel(signal)
            self.plot_widget.play()
        
        self.scrolling_x_axis_scrollbar.setMaximum(self.plot_widget.x_axis[-1])
        self.scrolling_x_axis_scrollbar.valueChanged.connect(lambda: self.plot_widget.scrolling_x_axis_scrollbar_effect(self.scrolling_x_axis_scrollbar.value()))
        # self.scrolling_x_axis_scrollbar.setValue(self.plot_widget.x_axis[-1])
        
        self.cine_scrollbar.sliderReleased.connect(lambda : self.plot_widget.cine_speed(self.cine_scrollbar.value()))# slider feature 
        
        self.scrolling_y_axis_scrollbar.setMinimum(self.plot_widget.min_signals_value)
        self.scrolling_y_axis_scrollbar.setMaximum(self.plot_widget.max_signals_value)
        self.scrolling_y_axis_scrollbar.valueChanged.connect(lambda: self.plot_widget.scrolling_y_axis_scrollbar_effect(self.scrolling_y_axis_scrollbar.value()))
        # self.scrolling_y_axis_scrollbar.valueChanged.connect(lambda: self.plot_widget.scrolling_y_axis_scrollbar_effect(self.current_y_axis_start_value))

        self.viewBox.sigRangeChanged.connect(self.set_sliders_value)
    
    def set_sliders_value(self , view,ranges):
        x_axis_slider_value = ranges[0][0]
        y_axis_slider_value = ranges[1][0]
        self.scrolling_x_axis_scrollbar.blockSignals(True)
        self.scrolling_x_axis_scrollbar.setValue(int(x_axis_slider_value))
        self.scrolling_x_axis_scrollbar.blockSignals(False)
        self.scrolling_y_axis_scrollbar.blockSignals(True)
        self.scrolling_y_axis_scrollbar.setValue(int(y_axis_slider_value))
        self.scrolling_y_axis_scrollbar.blockSignals(False)
        # self.current_x_axis_start_value = int(x_axis_slider_value)
        # print(x_axis_slider_value)
        # return
        # self.current_y_axis_start_value = int(y_axis_slider_value)
        

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
