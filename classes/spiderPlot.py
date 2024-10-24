# here we try to draw the graph (make an object that could import a CSV file based on the number of columns deside the dimentions of the graph)
import sys
from PyQt5.QtWidgets import QApplication, QColorDialog, QWidget, QVBoxLayout, QPushButton, QSpinBox, QHBoxLayout, QSlider, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint, QTimer
from math import cos, sin, pi, radians
import numpy as np
import pandas as pd

class SpiderPlot(QWidget):
    def __init__(self, data_samples:pd.DataFrame, time_slider):
        super().__init__()
        
        # Initial window setup
        self.data = data_samples
        self.time_slider = time_slider
        self.max_values = self.get_max_values(self.data)
        print(f'max values in the dataframes {self.max_values}')
        
        # Polygon properties
        self.radius = 250  # Radius for the circle in which the polygon is inscribed4
        print(f'shape of the data will be plotted{self.data.shape}')
        
        self.data_points, self.num_vertices = self.data.shape
        self.num_vertices = self.num_vertices-1
        self.axis_labels = self.data.columns[1:]
        
        self.polygon_pen = QPen(Qt.black, 2)
        self.axis_pen =  QPen(Qt.gray, 2)
        self.spider_pen =  QPen(Qt.white, 2)

        
  # Default number of vertices (triangle)
        self.current_row_idx = 0
        self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.time_interval = 100
        self.timer.start(self.time_interval)
        

    def get_max_values(self, data):
        max_values = []
        for col_name in data.columns[1:]:
            max_values.append(data[col_name].max())
        return max_values
    
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

        if self.current_row_idx >= self.time_slider.maximum():
            self.time_slider.setValue(self.time_slider.maximum())
        self.time_slider.setValue(self.current_row_idx)
        if self.current_row_idx <= self.time_slider.maximum():
            self.update()
            
    def repaint_animation(self,row = -1):  
        if row != -1:
            self.current_row =  self.data.loc[row, :].values.flatten().tolist()
            self.time_slider.setValue(self.current_row_idx)

            if self.current_row_idx >= self.time_slider.maximum():
                self.time_slider.setValue(self.time_slider.maximum())
            self.time_slider.setValue(self.current_row_idx)
            if self.current_row_idx <= self.time_slider.maximum():
                self.repaint()
            
    def paintEvent(self, event):
        # Initialize QPainter object
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate the center of the widget
        center_x = self.width() // 2
        center_y = self.height() // 2
                
        # Draw the polygon
        self.draw_axis_labels(painter, center_x, center_y)
        self.draw_polygon(painter, center_x, center_y)
        self.draw_grid(painter, center_x, center_y)
        self.draw_spider(painter,center_x, center_y)


    def draw_grid(self, painter, center_x, center_y, num_levels=5):
        grid_pen = QPen(Qt.gray, 2, Qt.DotLine)
        painter.setPen(grid_pen)
        angle_step = 2 * pi / self.num_vertices

        for level in range(num_levels):
            vertices = []
            r = (level/num_levels)*self.radius 
            for vertix in range(self.num_vertices):
                angle = vertix * angle_step
                x = int(center_x + r * cos(angle))
                y = int(center_y - r * sin(angle))  # Negative because of Qt's inverted y-axis
                vertices.append(QPoint(x, y))
                
            for vertix in range(self.num_vertices):
                next_vertex = vertices[(vertix + 1) % self.num_vertices]  # Wrap around to the first vertex
                painter.drawLine(vertices[vertix], next_vertex)

            
    def draw_polygon(self, painter, center_x, center_y):
        painter.setPen(self.polygon_pen)

        angle_step = 2 * pi / self.num_vertices
        vertices = []
        
        center = QPoint(center_x, center_y)

        # Calculate the coordinates for each vertex
        for vertix in range(self.num_vertices):
            angle = vertix * angle_step
            x = int(center_x + self.radius * cos(angle))
            y = int(center_y - self.radius* sin(angle))  # Negative because of Qt's inverted y-axis
            vertices.append(QPoint(x, y))

        # Draw lines between the vertices
        painter.drawPoint(center)
        for vertix in range(self.num_vertices):
            next_vertex = vertices[(vertix+1) % self.num_vertices]  # Wrap around to the first vertex
            painter.drawLine(vertices[vertix], next_vertex)
            painter.setPen(self.axis_pen)
            painter.drawLine(center,vertices[vertix])    
            painter.setPen(self.polygon_pen)

            

    def draw_spider(self, painter, center_x, center_y):
        spider_pen = self.spider_pen
        painter.setPen(spider_pen)
        values = self.current_row[1:]  
        vertices = []
        
        for vertix in range(self.num_vertices):
            normalized_value = values[vertix] / self.max_values[vertix]
            normalized_value = max(0, min(1, normalized_value))
            scaled_radius = self.radius * normalized_value
            x = int(center_x + scaled_radius * cos(angle))
            y = int(center_y - scaled_radius * sin(angle))  
            vertices.append(QPoint(x, y))

        for vertix in range(self.num_vertices):
            next_vertex = vertices[(vertix + 1) % self.num_vertices]
            painter.drawLine(vertices[vertix], next_vertex)
        
    def draw_axis_labels(self, painter, center_x, center_y):
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        angle_step = 2 * pi / self.num_vertices
        for i, label in enumerate(self.axis_labels):
            angle = i * angle_step
            x = int(center_x + (self.radius + 20) * cos(angle))
            y = int(center_y - (self.radius + 20) * sin(angle))
            formatted_value = f'{self.max_values[i]:.2f}'

            painter.drawText(x - 20, y, 80, 40, Qt.AlignCenter, f'{label}, {formatted_value}')


class PlotControls(QWidget):
    def __init__(self, PlayImage,PauseImage, SpiderPlot, backward_button, forward_button, speed_control, start_stop_button, replay_button, color_control_button, time_slider):
        super().__init__()
        
        self.spider_plot = SpiderPlot
        
        self.PlayImage = PlayImage
        self.PauseImage = PauseImage      

        self.start_stop_button = start_stop_button
        self.start_stop_button.clicked.connect(self.start_stop_plotting)
        
        self.color_control_button = color_control_button
        self.color_control_button.clicked.connect(self.change_spider_color)

        self.forward_button = forward_button
        self.forward_button.clicked.connect(self.forward_plotting)
        
        self.backward_button = backward_button
        self.backward_button.clicked.connect(self.backward_plotting)

        self.replay_button = replay_button
        self.replay_button.clicked.connect(self.replay_plotting)
        
        self.time_slider = time_slider
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(self.spider_plot.data_points -2) 
        self.time_slider.setValue(0)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(1)
        self.time_slider.valueChanged.connect(self.slider_changed)

        self.speed_slider = speed_control
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)  # Default speed
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed = 50
        self.start_stop_flag = False
        
    def start_plotting(self):
        self.spider_plot.timer.start(self.convert_speed_to_interval(self.speed))
        self.start_stop_button.setIcon(self.PauseImage)
        
    def stop_plotting(self):
        self.spider_plot.timer.stop()
        self.start_stop_button.setIcon(self.PlayImage)

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
        self.auto_update_slider()


    def backward_plotting(self):
    # Move backward one step in the data
        if self.spider_plot.current_row_idx > 0:
            self.spider_plot.current_row_idx -= 1
            self.spider_plot.repaint_animation(self.spider_plot.current_row_idx)  # Update the plot to reflect the new index
            self.auto_update_slider()

        # self.time_slider.setValue(self.spider_plot.current_row_idx)
    def replay_plotting(self):
            self.spider_plot.current_row_idx = 0
            self.start_plotting()
            self.time_slider.setValue(self.spider_plot.current_row_idx)

    def slider_changed(self):
        # Update the current row index based on the slider position
        self.spider_plot.current_row_idx = self.time_slider.value()
        self.spider_plot.repaint_animation(self.spider_plot.current_row_idx)

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

    
    
    def draw_new_graph(self):

            files, _ = QFileDialog.getOpenFileNames(self, "Open CSV Files", "", "CSV Files (*.csv)")
            csv_files = []
            # If files are selected, store the file paths
            if files:
                csv_files.extend(files)
                self.wave_instance = wave(files_directories = csv_files)
                print(f'CSV files:{csv_files}'  )
                self.horizontalLayout_15.removeWidget(self.graph)

                self.graph = SpiderPlot(self.wave_instance.data_samples, self.NonRectangleGraphTimeSlider)    
                self.spider_viewer_control = PlotControls(self.PlayImage, self.PauseImage ,self.graph, self.BackButtonNonRectangle, self.NextButtonNonRectangle, 
                                                    self.SpeedSliderNonRectangleGraph, self.PlayPauseNonRectangleButton, self.ReplayNonRectangleButton, self.ChangeColorButtonNonRectangle,self.NonRectangleGraphTimeSlider)
                self.horizontalLayout_15.addWidget(self.graph)

class phasorGraphPoint(QPoint):
    def __init__(self, phase, frequency, amplitude, index, radius, maximum, center_x, center_y):
        super().__init__()
        self.phase = phase
        self.frequency = frequency
        self.amplitude = amplitude
        self.index = index
        self.radius = radius
        self.max = maximum
        self.center_x = center_x
        self.center_y = center_y
        self.qpoint = [self.createQpoint()]
        
    def createQpoint(self):
        normalized_amplitude = self.amplitude / self.max
        normalized_amplitude = max(0, min(1, normalized_amplitude))
        
        scaled_radius = self.radius * normalized_amplitude
        
        x = int(self.center_x + scaled_radius * cos(self.phase))
        y = int(self.center_y - scaled_radius * sin(self.phase))
        self.setX(x)
        self.setY(y)
        
        return x,y

class PhasorGraph(QWidget):
        def __init__(self, data_path):
            super().__init__()
            print(f'CSV files:{data_path}'  )

            self.data = self.transform_ecg_to_amplitude_phase(data_path[0])
            print(f'sahpe {self.data.shape}, columns: {self.data.columns}')
            self.current_row_idx = 0
            self.current_batch_idx = 0
            self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()
            self.freq = self.data['Frequency']
            self.amp = self.data['Amplitude']
            self.phase = self.data['Phase']
            self.data_points= len(self.amp)
            
            self.current_points = []
            self.current_phase = 0
            
            print(f'frequincies:{self.freq}, ampllitudes: {self.amp}')
            
            self.max_amp = max(abs(self.amp))
            print(f'max ')
            print(f'max values in the dataframes {self.max_amp}')
            self.center_x = self.width() // 2
            self.center_y = self.height() // 2    
            self.radius = 250 
            
            self.all_batches = self.transform_data_to_qpoints(7, self.data_points//7 , self.center_x, self.center_y)
            print(f'shape of the data will be plotted{self.data.shape}')
            
  
            self.circle_pen = QPen(Qt.black, 2)
            self.inner_pen =  QPen(Qt.gray, 2, Qt.DotLine)
            self.point_pen =  QPen(Qt.white, 4)
            self.line_pen  =  QPen(Qt.white, 3, Qt.DotLine)
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_animation)
            self.time_interval = 100
            self.timer.start(self.time_interval)
        def add_point(self, new_point):
            if self.current_phase >= pi:
                point = self.current_points.pop(0)
                self.current_phase -=  point.phase
            self.current_points.append(new_point)
            self.current_phase += new_point.phase
            
            self.update_animation()
            
        def transform_ecg_to_amplitude_phase(self, file_path):
            data = pd.read_csv(file_path)
            print(f'data shape{data.shape}')
            time_values = data['time'].values
            ecg_values = data['value'].values
        
            fft_result = np.fft.fft(ecg_values)
            freqs = np.fft.fftfreq(len(ecg_values), d=(time_values[1] - time_values[0]))
            
            amplitude = np.abs(fft_result)
            phase = np.angle(fft_result)
            amplitude_phase_df = pd.DataFrame({'Frequency': freqs, 'Amplitude': amplitude, 'Phase': phase}) 
            amplitude_phase_df = amplitude_phase_df[amplitude_phase_df['Frequency'] >= 0].reset_index(drop=True)
            
            return amplitude_phase_df
        
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

            # if self.current_row_idx >= self.time_slider.maximum():
            #     self.time_slider.setValue(self.time_slider.maximum())
            # self.time_slider.setValue(self.current_row_idx)
            if self.current_row_idx <= len(self.data):
                self.update()
        def repaint_animation(self,row = -1):  
            if row != -1:
                self.current_row =  self.data.loc[row, :].values.flatten().tolist()
                # self.time_slider.setValue(self.current_row_idx)

                # if self.current_row_idx >= self.time_slider.maximum():
                #     self.time_slider.setValue(self.time_slider.maximum())
                # self.time_slider.setValue(self.current_row_idx)
                if self.current_row_idx <= len(self.data):
                    self.repaint()
                
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            self.draw_circle(painter, self.center_x, self.center_y, self.radius)
            self.draw_grid(painter, self.center_x, self.center_y)
            
            self.draw_phasor_point(painter,self.center_x, self.center_y)
            # self.draw_axis_labels(painter, center_x, center_y)
    
        def transform_data_to_qpoints(self, batch_size, num_batches, center_x, center_y):
            """
            Transforms data into batches of QPoint objects representing vertices for plotting.

            Parameters:
                batch_size (int): Number of points per batch.
                num_batches (int): Number of batches to generate.
                center_x (int): X-coordinate of the center.
                center_y (int): Y-coordinate of the center.

            Returns:
                List[List[QPoint]]: List of batches, each containing a list of QPoint objects.
            """
            all_batches = []

            for batch_index in range(num_batches):
                vertices = []

                for _ in range(batch_size):
                    # Get the current frequency, phase, and amplitude
                    current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()

                    freq = current_row[0]
                    phase = current_row[2]
                    amplitude = abs(current_row[1])

                    # Normalize the amplitude
                    max_amplitude = self.max_amp
                    normalized_amplitude = amplitude / max_amplitude
                    normalized_amplitude = max(0, min(1, normalized_amplitude))

                    # Scale the radius based on the normalized amplitude
                    scaled_radius = self.radius * normalized_amplitude

                    # Calculate the x and y coordinates
                    current_x = int(center_x + scaled_radius * cos(phase))
                    current_y = int(center_y - scaled_radius * sin(phase))

                    # Add the QPoint to the list
                    vertices.append(QPoint(current_x, current_y))

                # Add the current batch to the list of all batches
                all_batches.append(vertices)

            return all_batches
                 

        def frequency_to_color(self, frequency):
            # Map the frequency to a value between 0 and 1
            min_freq = min(self.freq)
            max_freq = max(self.freq)
            normalized_freq = (frequency - min_freq) / (max_freq - min_freq)
            
            # Interpolate between red (1,0,0) and blue (0,0,1)
            red = int(255 * (1 - normalized_freq))
            blue = int(255 * normalized_freq)
            
        # Create a QColor from the interpolated values
            return QColor(red, 0, blue)
        
        def draw_grid(self, painter, center_x, center_y, num_levels=5):
    # Create a dotted pen style for the circles
            painter.setPen(self.inner_pen)

            # Iterate over each level to draw circles with different radii
            for level in range(1, num_levels + 1):
                # Calculate the radius for this level
                r =int((level / num_levels) * self.radius)                
                # Draw a dotted circle with the current radius
                painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)
                
        def draw_circle(self, painter, center_x, center_y,  r):
            painter.setPen(self.circle_pen)
            painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)
            center = QPoint(center_x, center_y)
            painter.drawPoint(center)
         
        def drawtheseq(self, painter, center_x, center_y):
            painter.setPen(self.line_pen)
            
            for i in range(len(self.current_points)):
                if i > 0: 
                    painter.drawLine(self.current_points[i - 1], self.current_points[i])

                painter.setPen(self.point_pen)
                painter.drawPoint(self.current_points[i])
                painter.setPen(self.line_pen)


            if self.current_phase > pi:  
                point = self.points.pop(0)
                self.current_phase -= point.phase            
        
        # def draw_batches(self, painter, center_x, center_y):
        #     # Parameters for the transformation
        #     batch_size = 7
        #     num_batches = self.num_vertices//7
            
        #     # Get the list of batches of QPoints
            
        #     # Set the pen color based on the frequency
        #     current_row_freq =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()

        #     freq = current_row_freq[0]
        #     point_color = self.frequency_to_color(freq)
        #     self.point_pen.setColor(point_color)
        #     self.line_pen.setColor(point_color)

        #     # Draw each batch
        #     for i in range(len(self.all_batches[self.current_batch_idx])-1):
        #         current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()

        #         batch = self.all_batches[self.current_batch_idx]
        #         current_point = batch[i]
        #         next_vertex = batch[(i + 1) % len(batch)]  # Wrap around to the first vertex
        #         print(f'point:{batch[i]}, next: {next_vertex} ')
        #         painter.setPen(self.point_pen)
        #         painter.drawEllipse(batch[i].x() - 2, batch[i].y() - 2, 4, 4)

        #         painter.drawLine(current_point,next_vertex)
        #         # painter.setPen(self.point_pen)
        #         # self.update()
        #     self.current_batch_idx += 1

        
        def draw_phasor_point(self, painter, center_x, center_y):
            size = 7
            vertices =[]
            max_amplitude = self.max_amp
            freq = self.current_row[0]
            phase = self.current_row[2]
            amplitude = abs(self.current_row[1])
            normalized_amplitude = amplitude / max_amplitude
            normalized_amplitude = max(0, min(1, normalized_amplitude))
            
            scaled_radius = self.radius * normalized_amplitude
            
            self.current_x = int(center_x + scaled_radius * cos(phase))
            self.current_y = int(center_y - scaled_radius * sin(phase))
            
            current_point = QPoint(self.current_x, self.current_y)
            next_row =self.data.loc[self.current_row_idx+1, :].values.flatten().tolist()
            print(next_row)
            
            next_freq = next_row[0]
            next_phase = next_row[2]
            next_amplitude = abs(next_row[1])
            next_normalized_amplitude = next_amplitude / max_amplitude
            next_normalized_amplitude = max(0, min(1, next_normalized_amplitude))
            
            next_scaled_radius = self.radius * next_normalized_amplitude
            
            next_x = int(center_x + scaled_radius * cos(next_phase))
            next_y = int(center_y - scaled_radius * sin(next_phase))
            
            next_point = QPoint(next_x ,next_y)
            
            print(f'append{QPoint(self.current_x, self.current_y)}')
            point_color = self.frequency_to_color(freq)
            self.point_pen.setColor(point_color)
            self.line_pen.setColor(point_color)
            
            # painter.drawLine(QPoint(center_x, center_y), QPoint(self.current_x, self.current_y))
            painter.drawEllipse(self.current_x - 2, self.current_y - 2, 4, 4)
            painter.drawLine(current_point, next_point)
                
        def draw_axis_labels(self, painter, center_x, center_y):
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            freq = self.current_row[0]
            phase = self.current_row[2]  # Assuming the first column is phase
            amplitude = abs(self.current_row[1])

            formatted_value = f'amp: {amplitude:.2f}, freq:{freq:.2f} '

            painter.drawText(self.current_x - 20, self.current_y, 60, 20, Qt.AlignCenter, formatted_value)

class PhasorPlotControls(QWidget):
    def __init__(self, PlayImage,PauseImage, PhasorGraph, backward_button, forward_button, speed_control, start_stop_button, replay_button, color_control_button):
        super().__init__()
        
        self.widget = PhasorGraph
        
        self.PlayImage = PlayImage
        self.PauseImage = PauseImage      

        self.start_stop_button = start_stop_button
        self.start_stop_button.clicked.connect(self.start_stop_plotting)
        
        self.color_control_button = color_control_button
        self.color_control_button.clicked.connect(self.change_spider_color)

        self.forward_button = forward_button
        self.forward_button.clicked.connect(self.forward_plotting)
        
        self.backward_button = backward_button
        self.backward_button.clicked.connect(self.backward_plotting)

        self.replay_button = replay_button
        self.replay_button.clicked.connect(self.replay_plotting)
        
        # self.time_slider = time_slider
        # self.time_slider.setMinimum(0)
        # self.time_slider.setMaximum(self.widget.data_points -2) 
        # self.time_slider.setValue(0)
        # self.time_slider.setTickPosition(QSlider.TicksBelow)
        # self.time_slider.setTickInterval(1)
        # self.time_slider.valueChanged.connect(self.slider_changed)

        self.speed_slider = speed_control
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)  # Default speed
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.speed = 50
        self.start_stop_flag = False
        
    def start_plotting(self):
        self.widget.timer.start(self.convert_speed_to_interval(self.speed))
        self.start_stop_button.setIcon(self.PauseImage)
        
    def stop_plotting(self):
        self.widget.timer.stop()
        self.start_stop_button.setIcon(self.PlayImage)

    def start_stop_plotting(self):
        if self.start_stop_flag:
            self.start_plotting()
            self.start_stop_flag = False
            
        else: 
            self.stop_plotting()
            self.start_stop_flag = True

    def change_spider_color(self):
        color = QColorDialog.getColor()
        self.widget.point_pen.setColor(color)
        self.widget.line_pen.setColor(color)      
      

    def forward_plotting(self):
        # Move forward one step in the data            
        self.widget.current_row_idx = min(self.widget.current_row_idx + 1, self.widget.data_points - 1)
        self.widget.repaint_animation(self.widget.current_row_idx)
        self.widget.update_animation()



    def backward_plotting(self):
    # Move backward one step in the data
        if self.widget.current_row_idx > 0:
            
            self.widget.current_points.pop()
            self.widget.current_row_idx -= 2
            self.widget.repaint_animation(self.widget.current_row_idx)  # Update the plot to reflect the new index
            self.widget.update_animation()

        # self.time_slider.setValue(self.spider_plot.current_row_idx)
    def replay_plotting(self):
            self.widget.current_row_idx = 0
            self.widget.current_points = []
            self.start_plotting()
            # self.time_slider.setValue(self.widget.current_row_idx)

    # def slider_changed(self):
    #     # Update the current row index based on the slider position
    #     self.widget.current_row_idx = self.time_slider.value()
    #     self.widget.repaint_animation(self.widget.current_row_idx)
        
    # def auto_update_slider(self):
    #     # Update the slider position based on the current row index
    #     self.time_slider.setValue(self.widget.current_row_idx)
        
    def change_speed(self):
        # Adjust speed based on the slider value
        self.speed = self.speed_slider.value()
        if self.widget.timer.isActive():
            self.widget.timer.start(self.convert_speed_to_interval(self.speed))

    def convert_speed_to_interval(self, speed):
        # Convert speed (1-100) to time interval (10-1000 ms)
        return int(1010 - (speed * 10))

    