import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QHBoxLayout,QSlider,  QMainWindow,QLineEdit,  QStackedWidget, QPushButton,QComboBox,  QMessageBox, QWidget, QColorDialog, QFrame, QVBoxLayout, QFileDialog ,QScrollBar
from PyQt5.uic import loadUi
import pandas as pd 
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt5.QtGui import QIcon
import copy
from classes.spiderPlot import SpiderPlot
from classes.CSVLoader import CSVLoader
from classes.resampled_data import wave
from classes.spiderPlot import PlotControls
import CompiledImages  

class Nonrecatngular_Page(QMainWindow):
    def __init__(self):
        super(Nonrecatngular_Page, self).__init__()
        loadUi('main.ui', self)

        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Multi Signals Viewer')
        min_height = 900
        min_width = 1150

        self.setMinimumHeight(min_height)
        self.setMinimumWidth(min_width)

        self.PlayImage = QIcon(':/Images/playW.png')
        self.PauseImage = QIcon(':/Images/pauseW.png')
        self.HideImage = QIcon(':/Images/hideW.png')
        self.ShowImage = QIcon(':/Images/showW.png')
        self.RewindImage = QIcon(':/Images/rewind.png')
        self.NoRewindImage = QIcon(':/Images/noRewind.png')
        self.LinkImage = QIcon(':/Images/linkB.png')
        self.UnlinkImage = QIcon(':/Images/unlink.png')

        self.Pages = self.findChild(QStackedWidget, 'stackedWidget') 

        self.NonRectangleSignalButton = self.findChild(QPushButton, 'NonRectangleSignalButton')
        self.NonRectangleSignalButton.clicked.connect(self.go_to_non_rectangle_signal_page)

        self.BackHomeButton1 = self.findChild(QPushButton, 'BackHomeButton1')
        self.BackHomeButton1.clicked.connect(self.go_to_home_page)

        self.BackHomeButton2 = self.findChild(QPushButton, 'BackHomeButton2')
        self.BackHomeButton2.clicked.connect(self.go_to_home_page)

        self.BackHomeButton3 = self.findChild(QPushButton, 'BackHomeButton3')
        self.BackHomeButton3.clicked.connect(self.go_to_home_page)
        
        self.NonRectangleGraph = self.findChild(QFrame, 'NonRectangleGraph')
        
        self.UploadSignalNonRectangle= self.findChild(QPushButton, 'UploadSignalNonRectangle')
        self.non_rectangle_multiple_csv_loader = CSVLoader(self.UploadSignalNonRectangle)

        target_sampling_rate = 10  # The desired sampling rate
        interpolation_order = 'linear'  # Interpolation method, could be 'linear', 'quadratic', etc.
       
        wave_instance = wave(self.non_rectangle_multiple_csv_loader.csv_files, target_sampling_rate, interpolation_order)
        graph = SpiderPlot(wave_instance.data_samples)
        self.horizontalLayout_15 = self.findChild(QHBoxLayout, 'horizontalLayout_15')
        self.horizontalLayout_15.addWidget(graph)
        
        self.PlayPauseNonRectangleButton = self.findChild(QPushButton, 'PlayPauseNonRectangleButton')
        
        self.ReplayNonRectangleButton = self.findChild(QPushButton, 'ReplayNonRectangleButton')

        self.SpeedSliderNonRectangleGraph = self.findChild(QSlider,'SpeedSliderNonRectangleGraph')
        
        self.BackButtonNonRectangle = self.findChild(QPushButton, 'BackButtonNonRectangle')
        
        self.NextButtonNonRectangle = self.findChild(QPushButton, 'NextButtonNonRectangle')
        
        self.ChangeColorButtonNonRectangle = self.findChild(QPushButton, 'ChangeColorButtonNonRectangle')
        
        self.spider_viewer_control = PlotControls(graph, self.BackButtonNonRectangle, self.NextButtonNonRectangle, 
                                                  self.SpeedSliderNonRectangleGraph, self.PlayPauseNonRectangleButton, self.ReplayNonRectangleButton)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Nonrecatngular_Page()
    window.show()
    sys.exit(app.exec_())
