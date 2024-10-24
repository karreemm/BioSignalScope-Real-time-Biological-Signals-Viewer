import sys
from PyQt5.QtWidgets import QApplication, QColorDialog, QWidget, QVBoxLayout, QPushButton, QSpinBox, QHBoxLayout, QSlider, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QPoint, QTimer
from math import cos, sin, pi
import numpy as np
import pandas as pd

class PhasorGraph(QWidget):
    def __init__(self, data_path, pathFlag = True):
        super().__init__()
        print(f'CSV files:{data_path}')
        
        super().setFixedSize(400, 400)
        self.graph_type = 'Line'
        if self.graph_type == 'Line':
            self.data = pd.read_csv(data_path[0])
        else:
            self.data = self.transform_ecg_to_amplitude_phase(data_path[0])

        print(f'shape {self.data.shape}, columns: {self.data.columns}')
        self.current_row_idx = 0
        self.current_row = self.data.loc[self.current_row_idx, :].values.flatten().tolist()
        self.time = self.data['time']
        self.data, self.offset = self.shift_columns_to_positive_range(self.data)
        self.values = self.data['value']

        self.data_points = len(self.values)
        self.current_points = []
        self.current_phase = 0
        self.max_amp = max(self.values)

        # self.time_slider = time_slider
        print(f'max values in the dataframes {self.max_amp}')
        self.center_x = self.width() // 2
        self.center_y = self.height() // 2
        self.radius = 200

        print(f'shape of the data will be plotted {self.data.shape}')
        
        self.circle_pen = QPen(Qt.black, 2)
        self.inner_pen = QPen(Qt.gray, 2)
        self.point_pen = QPen(Qt.white, 4)
        self.line_pen = QPen(Qt.white, 3)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.time_interval = 100
        self.timer.start(self.time_interval)

    def add_point(self):
        freq = self.current_row[0]
        phase = self.current_row[0]
        amplitude = abs(self.current_row[1])  
        
        new_point = phasorGraphPoint(phase, freq, amplitude, self.current_row_idx, self.radius, self.max_amp, self.center_x, self.center_y)
        self.current_points.append(new_point)
        self.current_phase = new_point.phase
        print(self.current_phase)

    def shift_columns_to_positive_range(self, data: pd.DataFrame) -> pd.DataFrame:
        adjusted_data = data.copy()
        offset_values = []
        for col_name in adjusted_data.columns[1:]:
            min_value = adjusted_data[col_name].min()
            if min_value < 0:
                adjusted_data[col_name] += abs(min_value)
                offset_values.append(abs(min_value)) 
        return adjusted_data, offset_values

    def update_animation(self):
        self.current_row_idx += 1
        if self.current_row_idx >= self.data_points - 1:
            self.timer.stop()
            
        self.current_row = self.data.loc[self.current_row_idx, :].values.flatten().tolist()
        self.add_point()

        if self.current_phase >= 2* pi:
            self.current_points.pop(0)

        # if self.current_row_idx >= self.time_slider.maximum():
        #     self.time_slider.setValue(self.time_slider.maximum())
        # self.time_slider.setValue(self.current_row_idx)
        self.update()

    def repaint_animation(self, row=-1):
        if row != -1:
            self.current_row_idx = row
            self.current_row = self.data.loc[self.current_row_idx, :].values.flatten().tolist()
            
            # if self.current_row_idx < len(self.current_points):
            #     self.current_points.pop()
            # if self.current_phase >= 2* pi:
            #     self.current_points.pop(0)

        self.update()

    def transform_ecg_to_amplitude_phase(self, file_path):
        data = pd.read_csv(file_path)
        print(f'data shape {data.shape}')
        time_values = data['time'].values
        ecg_values = data['value'].values
        min_value = min(ecg_values)
        
        if min_value < 0:
            data['value'] += abs(min_value)

        min_time, max_time = time_values.min(), time_values.max()
        phase_values =  10000 * pi * (time_values - min_time)
        
        transformed_data = pd.DataFrame({
            'phase': phase_values,
            'amplitude': data['value']
        })

        return transformed_data

    def draw_grid(self, painter, center_x, center_y, num_levels=5):
        painter.setPen(self.inner_pen)
        for level in range(1, num_levels + 1):
            r = int((level / num_levels) * self.radius)
            painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)

    def draw_circle(self, painter, center_x, center_y, r):
        painter.setPen(self.circle_pen)
        painter.drawEllipse(center_x - r, center_y - r, 2 * r, 2 * r)
        center = QPoint(center_x, center_y)
        painter.drawPoint(center)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.draw_circle(painter, self.center_x, self.center_y, self.radius)
        self.draw_grid(painter, self.center_x, self.center_y)
        self.draw_phasor_point(painter, self.center_x, self.center_y)

    def draw_phasor_point(self, painter, center_x, center_y):
        if len(self.current_points) < 2:
            return

        for i in range(len(self.current_points) -1):
            current_point = self.current_points[i]
            if (i+1)< (len(self.current_points) -1):
            
                next_point = self.current_points[i + 1]

            # painter.setPen(self.line_pen)
            # painter.drawLine(current_point, next_point)
            
            painter.setPen(self.point_pen)
            painter.drawPoint(current_point)
            # painter.drawEllipse(current_point.x() - 2, current_point.y() - 2, 3, 3)

      
        # painter.drawEllipse(last_point.x() - 2, last_point.y() - 2, 4, 4)


class phasorGraphPoint(QPoint):
    def __init__(self, phase, frequency, amplitude, index, radius, maximum, center_x, center_y):
        super().__init__()
        self.phase = 2 * phase
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
        
        x = int(self.center_x + scaled_radius * cos( self.phase))
        y = int(self.center_y - scaled_radius * sin(self.phase))
        self.setX(x)
        self.setY(y)
        
        return x, y
