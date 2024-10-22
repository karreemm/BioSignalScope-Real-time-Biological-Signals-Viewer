# here we try to draw the graph (make an object that could import a CSV file based on the number of columns deside the dimentions of the graph)
import sys
from PyQt5.QtWidgets import QApplication, QColorDialog, QWidget, QVBoxLayout, QPushButton, QSpinBox, QHBoxLayout, QSlider, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint, QTimer
from math import cos, sin, pi, radians
import numpy as np
import pandas as pd


class PhasorGraph(QWidget):
        def __init__(self, data_path, time_slider):
            super().__init__()
            print(f'CSV files:{data_path}'  )
            
            super().setFixedSize(400, 400)

            self.data = self.transform_ecg_to_amplitude_phase(data_path[0])

            print(f'sahpe {self.data.shape}, columns: {self.data.columns}')
            self.current_row_idx = 0
            self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()
            self.freq = self.data['Frequency']
            self.amp = self.data['Amplitude']
            self.phase = self.data['Phase']
            self.data_points= len(self.amp)
            
            self.current_points = []
            self.current_phase = 0
            
            print(f'frequincies:{self.freq}, ampllitudes: {self.amp}')
            
            self.time_slider = time_slider
            self.max_amp = max(abs(self.amp))
            print(f'max ')
            print(f'max values in the dataframes {self.max_amp}')
            self.center_x = self.width() // 2
            self.center_y = self.height() // 2    
            self.radius = 200 
            
            print(f'shape of the data will be plotted{self.data.shape}')
            
            self.circle_pen = QPen(Qt.black, 2)
            self.inner_pen =  QPen(Qt.gray, 2, Qt.DotLine)
            self.point_pen =  QPen(Qt.white, 4)
            self.line_pen  =  QPen(Qt.white, 3, Qt.DotLine)
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_animation)
            self.time_interval = 100
            self.timer.start(self.time_interval)
            
            
        def add_point(self):
            freq = self.current_row[0]
            phase = self.current_row[2]
            amplitude = abs(self.current_row[1])  
            print(f'point: {phase}')          
            new_point = phasorGraphPoint(phase, freq, amplitude, self.current_row_idx, self.radius, self.max_amp, self.center_x, self.center_y)
            self.current_points.append(new_point)
            self.current_phase += new_point.phase
            # self.update_animation()
            # self.repaint_animation()
          
        def update_animation(self):  
            print(f'U phase{self.current_phase}')
    
            self.current_row_idx += 1
            if self.current_row_idx >= self.data_points - 1:
                self.timer.stop()           
            self.current_row =  self.data.loc[self.current_row_idx, :].values.flatten().tolist()
            self.add_point()

            if  len(self.current_points) > 7:  
                point = self.current_points.pop(0)
                self.current_phase -= point.phase  
                self.update()
                print('point deleted')
            if self.current_row_idx >= self.time_slider.maximum():
                self.time_slider.setValue(self.time_slider.maximum())
            self.time_slider.setValue(self.current_row_idx)
            if self.current_row_idx <= self.time_slider.maximum():
                self.update()
        def repaint_animation(self,row = -1):
            print(f'P phase{self.current_phase}')
  
            if row != -1:
                
                self.current_row =  self.data.loc[row, :].values.flatten().tolist()
                self.time_slider.setValue(self.current_row_idx)
                self.add_point()

                if len(self.current_points) > 7:  
                    point = self.current_points.pop(0)
                    self.current_phase -= point.phase 
                    print('point deleted')
                    
                    self.repaint()

                if self.current_row_idx >= self.time_slider.maximum():
                    self.time_slider.setValue(self.time_slider.maximum())
                self.time_slider.setValue(self.current_row_idx)

                    
        def transform_ecg_to_amplitude_phase(self, file_path):
            data = pd.read_csv(file_path)
            print(f'data shape{data.shape}')
            time_values = data['time'].values
            ecg_values = data['value'].values
        
            fft_result = np.fft.fft(ecg_values)
            freqs = np.fft.fftfreq(len(ecg_values), d=(time_values[1] - time_values[0]))

            amplitude = np.abs(fft_result)
            phase = abs(np.angle(fft_result))
            amplitude_phase_df = pd.DataFrame({'Frequency': freqs, 'Amplitude': amplitude, 'Phase': phase}) 
            amplitude_phase_df = amplitude_phase_df[amplitude_phase_df['Frequency'] >= 0].reset_index(drop=True)
            sorted_data = amplitude_phase_df.sort_values(by=['Frequency'], ascending= True).reset_index(drop=True)
            print(f'the data{sorted_data}')
            return sorted_data
        
        def get_speed(self):
            return 100*(1/(self.time_interval))
    
        def set_speed(self, speed):
            self.time_interval = speed
            self.timer.setInterval(self.time_interval) 
        
        def frequency_to_color(self, frequency):
            min_freq = min(self.freq)
            max_freq = max(self.freq)
            normalized_freq = (frequency - min_freq) / (max_freq - min_freq)
            red = int(255 * (1 - normalized_freq))
            blue = int(255 * normalized_freq)
            return QColor(red, 0, blue)
        
        def draw_grid(self, painter, center_x, center_y, num_levels=5):
            painter.setPen(self.inner_pen)
            for level in range(1, num_levels + 1):
                r =int((level / num_levels) * self.radius)                
                painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)
                
        def draw_circle(self, painter, center_x, center_y,  r):
            painter.setPen(self.circle_pen)
            painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)
            center = QPoint(center_x, center_y)
            painter.drawPoint(center)
           
       
        def paintEvent(self, event):
            print(self.current_row_idx)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            self.draw_circle(painter, self.center_x, self.center_y, self.radius)
            self.draw_grid(painter, self.center_x, self.center_y)
            
            self.drawtheseq(painter,self.center_x, self.center_y)
    
        
  
        def drawtheseq(self, painter, center_x, center_y):
            painter.setPen(self.line_pen)
            for i in range(len(self.current_points)):
                              
                self.point_pen.setColor(self.frequency_to_color(self.current_points[i].frequency))
                # self.draw_axis_labels(painter, self.current_points[i].x(), self.current_points[i].y())

                painter.setPen(self.point_pen)
                painter.drawEllipse(self.current_points[i].x() - 2, self.current_points[i].y() - 2, 4, 4)

                painter.setPen(self.line_pen)
                if i > 0: 
                    # painter.drawLine(self.current_points[i - 1], self.current_points[i])
                    painter.drawLine(QPoint(self.center_x, self.center_y), self.current_points[i])



          

        
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
                
        def draw_axis_labels(self, painter, x, y):
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)

            freq = self.current_row[0]
            phase = self.current_row[2]  # Assuming the first column is phase
            amplitude = abs(self.current_row[1])

            formatted_value = f'amp: {amplitude:.2f}, freq:{freq:.2f} '

            painter.drawText(x - 20, y, 60, 20, Qt.AlignCenter, formatted_value)



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
