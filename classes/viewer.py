from classes.channel_ import CustomSignal
import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
from math import inf

class Viewer(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.__channels = []
        self.__rewind_state = False
        self.__cine_speed = 10
        self.__zoom = 1
        
        self.x_axis = []
        
        self.play_state = True
        
        self.counter = 0
        self.time_window = 1000
        
        
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        self.play()
        
        
    def update_signal(self):
        if self.time_window + self.counter < len(self.x_axis):
            self.counter += 10
            for channel in self.__channels:
                self.plot(self.x_axis,channel.signal)
        else:
            self.counter = 0
        self.setXRange(min(self.x_axis[self.counter:self.counter + self.time_window]), max(self.x_axis[self.counter:self.counter + self.time_window])  )
            
        min_interval_value = inf
        max_interval_value = -inf
        # for channel in self.__channels:
        #     min_channel_interval_value = min(channel.signal[self.counter:self.counter + self.time_window])
        #     if min_channel_interval_value < min_interval_value:
        #         min_interval_value = min_channel_interval_value
        #     max_channel_interval_value = max(channel.signal[self.counter:self.counter + self.time_window])
        #     if max_channel_interval_value > max_interval_value:
        #         max_interval_value = max_channel_interval_value

        # self.setYRange(min_interval_value, max_interval_value)
            
    def play(self):
        self.play_state = True
        self.timer.start(self.__cine_speed)
        
    def pause(self):
        self.play_state = False
        self.timer.stop()
    
    def rewind(self):
        self.__linked_rewind_state = not self.__linked_rewind_state
        pass    
    
    def zoom_in(self):
        pass
    
    def zoom_out(self):
        pass
    
    def add_channel(self , new_channel):
        if isinstance(new_channel , CustomSignal):
            self.__channels.append(new_channel)
            self.x_axis = list(range(max([len(signal) for signal in self.__channels]))) ## max len in the signals imported
        else:
            raise Exception("The new channel must be of class CustomSignal")
    
    def remove_channel(self , to_be_removed_channel):
        self.__channels.remove(to_be_removed_channel)
    
    
    @property
    def cine_speed(self):
        return self.__cine_speed
    
    @cine_speed.setter
    def cine_speed(self , new_speed):
        """
        new_speed: the input must range between 10 and 50 
        """
        if(new_speed > 0):
            self.__cine_speed = new_speed
            self.pause()
            self.play()
        else: 
            raise Exception("Speed of cine must be greater than zero")
        pass
    
    @property
    def rewind_state(self):
        return self.__rewind_state
    
    # @rewind_state.setter
    # def rewind_state(self, new_rewind_state):
    #     self.__rewind_state = new_rewind_state
    
    @property
    def channels(self):
        return self.__channels
    
    @property
    def zoom(self):
        return self.__zoom
    
    @zoom.setter
    def zoom(self , new_zoom):
        if(new_zoom > 0 ):
            self.__zoom = new_zoom
        else:
            raise Exception("Value of zoom must be greater than zero")
