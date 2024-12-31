import requests
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
import validators
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QProcess

class RealTimeSignal:
    def __init__(self):
        self.PlayImage = QIcon(':/Images/playW.png')
        self.PauseImage = QIcon(':/Images/pauseW.png')

        self.is_playing = False
        self.setDisabled = False

        self.x = list(range(1))  
        self.y = [0] * 1
        self.timer = QTimer()
        self.timer.setInterval(500) 
        self.timer.timeout.connect(self.update_plot_data)

    def initialize(self, RealTimeSignalInput, PlayPauseButtonRealTime, RealTimeScroll, graphWidget ,Pages , RealTimeSignalPage, MainPage):
        self.RealTimeSignalInput = RealTimeSignalInput
        self.PlayPauseButtonRealTime = PlayPauseButtonRealTime
        self.RealTimeScroll = RealTimeScroll
        self.graphWidget = graphWidget
        self.RealTimeSignalPage = RealTimeSignalPage
        self.Pages = Pages
        self.MainPage = MainPage

        self.data_line = self.graphWidget.plot(self.x, self.y)
        self.PlayPauseButtonRealTime.setIcon(self.PlayImage)
        self.graphWidget.setMouseEnabled(x=False, y=False) 
        
        self.graphWidget.setMouseEnabled(x=False, y=False) 
    def validate_api_link(self):
        is_text_valid_api_link = validators.url(self.RealTimeSignalInput.text())
        if(is_text_valid_api_link):
            self.timer.start()
            self.PlayPauseButtonRealTime.setIcon(self.PauseImage)
            self.is_playing = not self.is_playing
        
    def show_real_time_graph(self):
        self.timer.start()

    def update_plot_data(self):        
        api_link = self.RealTimeSignalInput.text()
        if not api_link:
            return

        try:
            response = requests.get(api_link, timeout = 2)
            data = response.json()
            price = float(data['bpi']['USD']['rate'].replace(',', ''))

            self.y.append(price)
            # self.adjust_y_range()

            if len(self.x) < len(self.y):
                self.x.append(self.x[-1] + 1)

            self.data_line.setData(self.x, self.y)    
            self.RealTimeScroll.setRange(0, len(self.y) - 20)
            self.RealTimeScroll.setRange(0, max(0, len(self.y) - 20))
            self.RealTimeScroll.setValue(len(self.y) - 20)

            self.adjust_y_range()

        except Exception as e:
            print(f"Error fetching data: {e}")   
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Internet Disconnected")
            msg.setInformativeText("Please check your internet connection.")
            msg.setWindowTitle("Error")
            msg.setMinimumWidth(800)
            msg.setFixedWidth(800)
            msg.setStandardButtons(QMessageBox.Ok)
            result = msg.exec_()
            
            if result == QMessageBox.Ok:
                if self.MainPage != -1:
                    self.Pages.setCurrentIndex(self.MainPage)
                    self.timer.stop()
    def toggle_play_pause_real_time(self):
        if self.is_playing:
            self.timer.stop()
            self.PlayPauseButtonRealTime.setIcon(self.PlayImage)
        else:
            self.timer.start()
            self.PlayPauseButtonRealTime.setIcon(self.PauseImage)
        self.is_playing = not self.is_playing

    def scroll_graph(self, value):
        self.graphWidget.setXRange(value, value + 20)
    
    def go_to_real_time_page(self):
        if self.RealTimeSignalPage != -1:
            self.Pages.setCurrentIndex(self.RealTimeSignalPage)
            self.is_playing = False
            api_link = self.RealTimeSignalInput.text()
            self.RealTimeSignalInput.clear()
            self.RealTimeSignalInput.setText(api_link)
    def adjust_y_range(self):
        self.graphWidget.setYRange(67200, 68700)

    # API Link: https://api.coindesk.com/v1/bpi/currentprice.json
