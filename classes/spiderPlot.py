# here we try to draw the graph (make an object that could import a CSV file based on the number of columns deside the dimentions of the graph)
import sys
from PyQt5.QtWidgets import QApplication, QColorDialog, QWidget, QVBoxLayout, QPushButton, QSpinBox, QHBoxLayout, QSlider, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QTimer
from math import cos, sin, pi, radians

import pandas as pd

class SpiderPlot(QWidget):
    def __init__(self, data_samples:pd.DataFrame):
        super().__init__()
        
        # Initial window setup
        self.data = data_samples
        
        self.max_values = self.get_max_values(self.data)
        print(f'max values in the dataframes {self.max_values}')
        # Polygon properties
        self.radius = 200  # Radius for the circle in which the polygon is inscribed4
        print(f'shape of the data will be plotted{self.data.shape}')
        self.data_points, self.num_vertices = self.data.shape
        self.num_vertices = self.num_vertices-1
        self.axis_labels = self.data.columns[1:]
        self.polygon_pen = QPen(Qt.black, 2)
        self.axis_pen =  QPen(Qt.gray, 2)
        self.spider_pen =  QPen(Qt.black, 2)

        
  # Default number of vertices (triangle)
        self.current_row_idx = 0
        self.current_row =  self.data.loc[0, :].values.flatten().tolist()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.time_interval = 100
        self.timer.start(self.time_interval)
        

    def get_max_values(self, data):
        maximums = []
        for col_name in data.columns[1:]:
            maximums.append(data[col_name].max())
        return maximums
    
    def get_speed(self):
        return 100*(1/(self.time_interval))
    
    def set_speed(self, speed):
        self.time_interval = speed
        self.timer.setInterval(self.time_interval)
        

    def update_animation(self):      
        self.current_row_idx += 1
        if self.current_row_idx >= self.data_points - 1:
            self.timer.stop()           
        self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()
        self.update()
    def repaint_animation(self,row = -1):  
        if row != -1:
            self.current_row =  self.data.loc[row, :].values.flatten().tolist()
            self.repaint()
   
        # self.current_row_idx += 1
        # if self.current_row_idx >= self.data_points - 1:
        #     self.current_row_idx = 0
        # self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()
        

            
    def paintEvent(self, event):
        # Initialize QPainter object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the pen for the polygon lines
        # pen = QPen(Qt.black, 3)
        # painter.setPen(pen)
        
        # Calculate the center of the widget
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        print(f'{center_x}, {center_y}')
        
        # Draw the polygon
        self.draw_axis_labels(painter, center_x, center_y)
        self.draw_polygon(painter, center_x, center_y)
        self.draw_grid(painter, center_x, center_y)

        self.draw_spider(painter,center_x, center_y)


    def draw_grid(self, painter, center_x, center_y, num_levels=5):
        grid_pen = QPen(Qt.gray, 2, Qt.DotLine)
        painter.setPen(grid_pen)

        angle_step = 2 * pi / self.num_vertices
        
        center = QPoint(center_x, center_y)

        
        for i in range(num_levels):
            vertices = []

            r = (i/num_levels)*self.radius 
            for i in range(self.num_vertices):
                angle = i * angle_step
                x = int(center_x + r * cos(angle))
                y = int(center_y - r * sin(angle))  # Negative because of Qt's inverted y-axis
                vertices.append(QPoint(x, y))
            # Draw concentric circles
            step = self.radius / num_levels
            for i in range(self.num_vertices):
                next_vertex = vertices[(i + 1) % self.num_vertices]  # Wrap around to the first vertex
                painter.drawLine(vertices[i], next_vertex)

            
    def draw_polygon(self, painter, center_x, center_y):
        painter.setPen(self.polygon_pen)

        angle_step = 2 * pi / self.num_vertices
        vertices = []
        
        center = QPoint(center_x, center_y)

        # Calculate the coordinates for each vertex
        for i in range(self.num_vertices):
            angle = i * angle_step
            x = int(center_x + self.radius * cos(angle))
            y = int(center_y - self.radius* sin(angle))  # Negative because of Qt's inverted y-axis
            vertices.append(QPoint(x, y))
            # vertices.append(QPoint(-x, -y))

        # Draw lines between the vertices
        painter.drawPoint(center)
        for i in range( self.num_vertices):
            next_vertex = vertices[(i+1) % self.num_vertices]  # Wrap around to the first vertex
            painter.drawLine(vertices[i], next_vertex)
            painter.setPen(self.axis_pen)
            painter.drawLine(center,vertices[i])    
            painter.setPen(self.polygon_pen)

            

    def draw_spider(self, painter, center_x, center_y):
        spider_pen = self.spider_pen
        painter.setPen(spider_pen)
        
        # Calculate the angle between each vertex
        values = self.current_row[1:]  # Exclude the 'time' column
        angle_step = 2 * pi / self.num_vertices

        # List to store vertices
        vertices = []
        
        # Calculate the coordinates for each vertex
        for i in range(self.num_vertices):
            angle = i * angle_step
            # Normalize the value to be between 0 and 1
            normalized_value = values[i] / self.max_values[i]
            
            # Ensure normalized_value is clamped between 0 and 1
            normalized_value = max(0, min(1, normalized_value))
            
            # Scale the radius based on the normalized value
            scaled_radius = self.radius * normalized_value
            
            x = int(center_x + scaled_radius * cos(angle))
            y = int(center_y - scaled_radius * sin(angle))  # Negative because of Qt's inverted y-axis
            vertices.append(QPoint(x, y))
            
        # Draw lines between the vertices
        for i in range(self.num_vertices):
            next_vertex = vertices[(i + 1) % self.num_vertices]  # Wrap around to the first vertex
            painter.drawLine(vertices[i], next_vertex)
        
    def draw_axis_labels(self, painter, center_x, center_y):
        font = painter.font()
        font.setPointSize(6)
        painter.setFont(font)

        angle_step = 2 * pi / self.num_vertices
        for i, label in enumerate(self.axis_labels):
            angle = i * angle_step
            x = int(center_x + (self.radius + 20) * cos(angle))
            y = int(center_y - (self.radius + 20) * sin(angle))
            formatted_value = f'{self.max_values[i]:.2f}'

            painter.drawText(x - 20, y, 60, 20, Qt.AlignCenter, f'{label}, {formatted_value}')


class PlotControls(QWidget):
    def __init__(self, SpiderPlot, backward_button, forward_button, speed_control, start_stop_button, replay_button, color_control_button):
        super().__init__()
        
        self.spider_plot = SpiderPlot
        
        self.setWindowTitle("Spider Plot Control Panel")
        self.setGeometry(200, 200, 800, 600)
        
        main_layout = QVBoxLayout()
        plot_layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        

        self.start_stop_button = start_stop_button
        self.start_stop_button.clicked.connect(self.start_stop_plotting)
        # control_layout.addWidget(self.start_button)
        
        # self.stop_button = QPushButton("Stop")
        # self.stop_button.clicked.connect(self.stop_plotting)
        # control_layout.addWidget(self.stop_button)
        self.color_control_button = color_control_button
        self.color_control_button.clicked.connect(self.change_spider_color)

        
        self.forward_button = forward_button
        self.forward_button.clicked.connect(self.forward_plotting)
        
        self.backward_button = backward_button
        self.backward_button.clicked.connect(self.backward_plotting)

        self.replay_button = replay_button
        self.replay_button.clicked.connect(self.replay_plotting)
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(self.spider_plot.data_points - 1)
        self.time_slider.setValue(0)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(1)
        self.time_slider.valueChanged.connect(self.slider_changed)
        control_layout.addWidget(self.time_slider)

        self.speed_slider = speed_control
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)  # Default speed
        self.speed_slider.valueChanged.connect(self.change_speed)
              
        self.speed = 50
        self.start_stop_flag = False
    def start_plotting(self):
        self.spider_plot.timer.start(self.convert_speed_to_interval(self.speed))

    def stop_plotting(self):
        self.spider_plot.timer.stop()
        
    def start_stop_plotting(self):
        if self.start_stop_flag:
            self.start_plotting()
            self.start_stop_flag = False
        else: 
            self.stop_plotting()
            self.start_stop_flag = True

    def change_spider_color(self):
        color = QColorDialog.getColor()

        self.spider_plot.spider_pen.setColor(color)      


    def forward_plotting(self):
        # Move forward one step in the data            
        self.spider_plot.current_row_idx = min(self.spider_plot.current_row_idx + 1, self.spider_plot.data_points - 1)
        self.spider_plot.repaint_animation(self.spider_plot.current_row_idx)
        # self.time_slider.setValue(self.spider_plot.current_row_idx)
        self.auto_update_slider()


    def backward_plotting(self):
    # Move backward one step in the data
        if self.spider_plot.current_row_idx > 0:
            self.spider_plot.current_row_idx -= 1
            self.spider_plot.repaint_animation(self.spider_plot.current_row_idx)  # Update the plot to reflect the new index
            # self.time_slider.setValue(self.spider_plot.current_row_idx)

        # self.time_slider.setValue(self.spider_plot.current_row_idx)
    def replay_plotting(self):
            self.spider_plot.current_row_idx = 0
            self.start_plotting()
    def slider_changed(self, value):
        # Update the current row index based on the slider position
        self.spider_plot.current_row_idx = value
        self.spider_plot.update()

    def auto_update_slider(self):
        # Update the slider position based on the current row index
        self.time_slider.setValue(self.spider_plot.current_row_idx)
        
    def change_speed(self):
        # Adjust speed based on the slider value
        self.speed = self.speed_slider.value()
        if self.spider_plot.timer.isActive():
            self.spider_plot.timer.start(self.convert_speed_to_interval(self.speed))

    def convert_speed_to_interval(self, speed):
        # Convert speed (1-100) to time interval (10-1000 ms)
        return int(1010 - (speed * 10))

    
    