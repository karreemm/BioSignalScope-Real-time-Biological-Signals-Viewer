from classes.channel_ import CustomSignal
import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
import numpy as np
from math import inf

class Viewer(pg.PlotWidget):
    def __init__(self):
        super().__init__()
        self.__channels = []
        self.__rewind_state = False
        self.__cine_speed = 30
        self.__zoom = 1
        
        self.x_axis = []
        
        self.drag_active = False  
        
        self.play_state = False
        
        self.viewBox = self.getViewBox()
        
        self.y_axis_scroll_bar_enabled = False 
        
        self.counter = 0
        self.time_window = 1000
        
        self.max_signals_value = -inf
        self.min_signals_value = inf    
        
        self.scrolling_in_y_axis = False
        
        ## range trackers
        self.x_range_tracker_min, self.x_range_tracker_max = 0,1000
        self.y_range_tracker_min, self.y_range_tracker_max = 0,1000
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_signal)
        # self.play()
        
        
        
    def show_glue_rectangle_func(self):
            self.gluing_selected_region = pg.LinearRegionItem(values=[self.viewRange()[0][0]+50,self.viewRange()[0][0]+150])
            self.addItem(self.gluing_selected_region)
    def process_region_coord(self , selected_channel_index):
        selected_region = self.gluing_selected_region.getRegion()   
        # print(selected_region)  
        data_y = self.channels[selected_channel_index].signal[int(selected_region[0]): int(selected_region[1])]
        data_x = np.linspace(int(selected_region[0]) , int(selected_region[1]) , num= int(selected_region[1]) - int(selected_region[0]))
        return [data_x , data_y]
        
    def update_signal(self):
        if self.time_window + self.counter < len(self.x_axis):
            self.counter += 20
            # print(f"{self.viewRange()} range in updating")
        else:
            self.counter = 0
        self.setXRange(min(self.x_axis[self.counter:self.counter + self.time_window]), max(self.x_axis[self.counter:self.counter + self.time_window])  )
        # self.setXRange(self.viewRange()[0][0]+self.counter, self.viewRange()[0][1]+self.counter)
            
        min_interval_value = inf
        max_interval_value = -inf
        for channel in self.__channels:
            if self.counter + self.time_window > len(channel):
                continue
            min_channel_interval_value = min(channel.signal[self.counter:self.counter + self.time_window])
            if min_channel_interval_value < min_interval_value:
                min_interval_value = min_channel_interval_value
            max_channel_interval_value = max(channel.signal[self.counter:self.counter + self.time_window])
            if max_channel_interval_value > max_interval_value:
                max_interval_value = max_channel_interval_value

        # self.setYRange(min_interval_value, max_interval_value)
        if self.y_axis_scroll_bar_enabled:
            self.viewBox.setMouseEnabled(x = True, y =True)
            self.viewBox.enableAutoRange(x=False, y=False)
            self.viewBox.setAutoVisible(x=False, y=False)
            pass
        else:
            self.viewBox.setMouseEnabled(x = True, y =False)
            self.viewBox.enableAutoRange(x=False, y=True)
            self.viewBox.setAutoVisible(x=False, y=True)
        # self.setYRange(min_interval_value, max_interval_value)
        self.x_range_tracker_min, self.x_range_tracker_max = self.viewRange()[0][0], self.viewRange()[0][1]
        self.y_range_tracker_min, self.y_range_tracker_max = self.viewRange()[1][0], self.viewRange()[1][1]
            
    def play(self):
        if self.play_state == False:
            self.play_state = True
            self.timer.start(self.__cine_speed)
            # print(self.__cine_speed)
        if self.y_axis_scroll_bar_enabled:
            self.viewBox.setMouseEnabled(x = True, y =True)
            
            self.viewBox.enableAutoRange(x=False, y=False)
            self.viewBox.setAutoVisible(x=False, y=False)
        else:
            self.viewBox.setMouseEnabled(x = True, y =False)
            self.viewBox.enableAutoRange(x=False, y=True)
            self.viewBox.setAutoVisible(x=False, y=True)
            # self.setYRange(self.viewRange()[1][0], self.viewRange()[1][1])
        self.setXRange(self.viewRange()[0][0]+50, self.viewRange()[0][0]+1000)
        self.counter = int(max(0,self.viewRange()[0][0]))
            # print(f"{self.counter} this is counter from the play")
        self.setLimits(xMin = 0, xMax = self.x_axis[-1],  yMin = self.min_signals_value, yMax = self.max_signals_value)
            # , yMin = self.min_signals_value, yMax = self.max_signals_value
        
        # print(f'{self.viewRange()} mm')
        
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
            for channel in self.__channels:
                self.plot( [i for i in  range(len(channel.signal))] ,channel.signal, pen = pg.mkPen(color = channel.color))## pass the x_axis from the length of the signal
                print(channel.color)
                if min(channel.signal) < self.min_signals_value:
                    self.min_signals_value = min(channel.signal)
                if max(channel.signal) > self.max_signals_value:
                    self.max_signals_value = max(channel.signal)
        else:
            raise Exception("The new channel must be of class CustomSignal")
        
    def plot_internal_signals(self):
        for channel in self.__channels:
                self.plot( [i for i in  range(len(channel.signal))] ,channel.signal, pen = pg.mkPen(color = channel.color))## pass the x_axis from the length of the signal
                print(channel.color)
                if min(channel.signal) < self.min_signals_value:
                    self.min_signals_value = min(channel.signal)
                if max(channel.signal) > self.max_signals_value:
                    self.max_signals_value = max(channel.signal)
        
    def add_glued_moving_channel(self , new_channel , channel_x_values):
        if isinstance(new_channel , CustomSignal):
            self.__channels.append(new_channel)
            # self.x_axis = list(range(max([len(signal) for signal in self.__channels]))) ## max len in the signals imported
            self.plot( channel_x_values ,new_channel.signal)## pass the x_axis from the length of the signal
        else:
            raise Exception("The new channel must be of class CustomSignal")
    
    def remove_channel(self , to_be_removed_channel):
        self.__channels.remove(to_be_removed_channel)
    
    def scrolling_x_axis_scrollbar_effect(self , slidebar_current_value):
            self.blockSignals(True)
            self.setXRange(slidebar_current_value, slidebar_current_value+1000)
            self.blockSignals(False)
            
    def scrolling_y_axis_scrollbar_effect(self , slidebar_current_value):
            # self.blockSignals(True)
            self.viewBox.blockSignals(True)  # Block signals to avoid auto-ranging
            self.viewBox.setMouseEnabled(x = False, y =False)
            self.viewBox.enableAutoRange(x=False, y=True)
            self.viewBox.setAutoVisible(x=False, y=True)
            self.scrolling_in_y_axis = True
            self.setYRange(slidebar_current_value - 100, slidebar_current_value + 100)
            # self.setYRange(max = slidebar_current_value + self.viewRange()[1][1] -  self.viewRange()[1][0], min =slidebar_current_value)
            self.scrolling_in_y_axis = False
            self.viewBox.setMouseEnabled(x = True, y =True)
            self.viewBox.enableAutoRange(x=False, y=False)
            self.viewBox.setAutoVisible(x=False, y=False)
            self.viewBox.blockSignals(False)  # Unblock after setting the range
            # self.blockSignals(False)
        
    @property
    def cine_speed(self):
        return self.__cine_speed
    
    # @cine_speed.setter
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
        
    def drag_and_move(self):
        self.drag_active = True
        print("draging")
        # super().dragMoveEvent(event)  # Call the base class implementation if needed
    
    def reset_drag_flag(self):
        """Reset drag flag to False after the event."""
        self.drag_active = False
        
    # @property
    # def scrollbar_value(self):
    #     return self.__scrollbar_value
    
    # @scrollbar_value.setter
    # def scrollbar_value(self , new_scrollbar_value):
    #     self.__scrollbar_value = new_scrollbar_value
