import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit,  QStackedWidget, QPushButton,QComboBox,  QMessageBox, QWidget, QColorDialog, QFrame, QVBoxLayout, QFileDialog ,QScrollBar
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from classes.viewer import Viewer
from classes.channel_ import CustomSignal
from classes.gluer import Gluer
import pandas as pd 
import numpy as np
import pyqtgraph as pg

def compile_qrc():
    qrc_file = 'Images.qrc'
    output_file = 'CompiledImages.py'
    try:
        subprocess.run(['pyrcc5', qrc_file, '-o', output_file], check=True)
        print(f"Compiled {qrc_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to compile {qrc_file}: {e}")

compile_qrc()

import CompiledImages  

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
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

        self.is_rewinding_graph1 = False
        self.is_rewinding_graph2 = False

        self.is_playing_graph1 = False  
        self.is_playing_graph2 = False  

        self.is_graph1_visible = True
        self.is_graph2_visible = True

        self.Pages = self.findChild(QStackedWidget, 'stackedWidget') 

        self.NonRectangleSignalButton = self.findChild(QPushButton, 'NonRectangleSignalButton')
        self.NonRectangleSignalButton.clicked.connect(self.go_to_non_rectangle_signal_page)

        self.BackHomeButton1 = self.findChild(QPushButton, 'BackHomeButton1')
        self.BackHomeButton1.clicked.connect(self.go_to_home_page)

        self.BackHomeButton2 = self.findChild(QPushButton, 'BackHomeButton2')
        self.BackHomeButton2.clicked.connect(self.go_to_home_page)

        self.PlayPauseButtonGraph1 = self.findChild(QPushButton, 'PlayPauseButtonGraph1')
        self.PlayPauseButtonGraph1.clicked.connect(self.play_pause_graph1)
        self.PlayPauseButtonGraph1.setIcon(self.PauseImage)  

        self.PlayPauseButtonGraph2 = self.findChild(QPushButton, 'PlayPauseButtonGraph2')
        self.PlayPauseButtonGraph2.clicked.connect(self.play_pause_graph2)
        self.PlayPauseButtonGraph2.setIcon(self.PauseImage)  

        self.ShowHideButtonGraph1 = self.findChild(QPushButton, 'ShowHideButtonGraph1')
        self.ShowHideButtonGraph1.setIcon(self.HideImage)
        self.ShowHideButtonGraph1.clicked.connect(self.show_hide_graph1)

        self.ShowHideButtonGraph2 = self.findChild(QPushButton, 'ShowHideButtonGraph2')
        self.ShowHideButtonGraph2.setIcon(self.HideImage)
        self.ShowHideButtonGraph2.clicked.connect(self.show_hide_graph2)

        self.ColorButtonGraph1 = self.findChild(QPushButton, 'ColorButtonGraph1')
        self.ColorButtonGraph1.clicked.connect(self.change_color_graph1)  

        self.ColorButtonGraph2 = self.findChild(QPushButton, 'ColorButtonGraph2')
        self.ColorButtonGraph2.clicked.connect(self.change_color_graph2) 

        self.StartGluingButton = self.findChild(QPushButton, 'StartGluingButton')
        self.StartGluingButton.setEnabled(False) 
        self.StartGluingButton.clicked.connect(self.start_gluing)

        self.GluingModeButton = self.findChild(QPushButton, 'GluingModeButton')
        self.GluingModeButton.clicked.connect(self.gluing_mode)

        self.UpdateGluingButton = self.findChild(QPushButton , "UpdateGluingButton")
        self.UpdateGluingButton.clicked.connect(self.update_gluing_interpolate)
        
        self.MoveSignalLeftButton = self.findChild(QPushButton , "pushButton_2")
        self.MoveSignalLeftButton.clicked.connect(self.move_signal_left)

        self.RewindButtonGraph1 = self.findChild(QPushButton, 'RewindButtonGraph1')
        self.RewindButtonGraph1.setIcon(self.NoRewindImage)
        self.RewindButtonGraph1.clicked.connect(self.rewind_graph1)

        self.RewindButtonGraph2 = self.findChild(QPushButton, 'RewindButtonGraph2')
        self.RewindButtonGraph2.setIcon(self.NoRewindImage)
        self.RewindButtonGraph2.clicked.connect(self.rewind_graph2)
        
        # Adding functionality of going to glue window button
        self.StartGluingButton.clicked.connect(self.start_gluing)
        self.signal_gluing_page = self.findChild(QWidget, 'SignalGluing')
        self.page_index = self.Pages.indexOf(self.signal_gluing_page)
        self.glued_viewer_frame = self.signal_gluing_page.findChild(QFrame, 'GluingFrame')
        self.glued_frame_layout = QVBoxLayout()
        self.glued_viewer = Viewer()
        self.glued_frame_layout.addWidget(self.glued_viewer)
        self.glued_viewer_frame.setLayout(self.glued_frame_layout)
        self.y_interpolated = None
        
        data = ["25.4", "3.2", "120", "5.1", "30.9"]

        for column, value in enumerate(data):
            item = QtWidgets.QTableWidgetItem(value)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable) 
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)  
            self.tableWidget.setItem(0, column, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False) 
        self.tableWidget.horizontalHeader().setVisible(True)
        
        # initializing the main viewers 
        self.viewer_frame1 = self.findChild(QFrame, 'Graph1Frame')
        self.frame1_layout = QVBoxLayout()
        self.viewer1 = Viewer()
        self.frame1_layout.addWidget(self.viewer1)
        self.viewer_frame1.setLayout(self.frame1_layout)
        self.play_pause_graph1()
        
        self.viewer_frame2 = self.findChild(QFrame, 'Graph2Frame')
        self.frame2_layout = QVBoxLayout()
        self.viewer2 = Viewer()
        self.frame2_layout.addWidget(self.viewer2)
        self.viewer_frame2.setLayout(self.frame2_layout)
        self.play_pause_graph2()
        
        # initializing the buttons
        self.number_of_viewer_1_signals = 0
        self.number_of_viewer_2_signals = 0
        ## upload buttons
        self.upload_button_1 = self.findChild(QPushButton ,'BrowseButtonGraph1')
        self.upload_button_1.clicked.connect(lambda : self.load_signal('1'))
        self.upload_button_2 = self.findChild(QPushButton ,'BrowseButtonGraph2')
        self.upload_button_2.clicked.connect(lambda : self.load_signal('2'))
        
        # Auto fit mode 
        self.view_modes_dropdown_1 = self.findChild(QComboBox, 'ModeComboBoxGraph1')
        self.view_modes_dropdown_1.currentIndexChanged.connect(lambda index : self.change_view_mode(index, '1'))
        self.change_view_mode(0, '1')
        self.view_modes_dropdown_2 = self.findChild(QComboBox, 'ModeComboBoxGraph2')
        self.view_modes_dropdown_2.currentIndexChanged.connect(lambda index : self.change_view_mode(index, '2'))
        self.change_view_mode(0, '2')
        
        # initializing the signals dropdown 
        self.signals_dropdown_1 = self.findChild(QComboBox, 'SignalsComboBoxGraph1')
        for i in range(3):
            self.signals_dropdown_1.removeItem(0)
        # self.signals_dropdown_1.currentIndexChanged.connect(lambda:self.fill_signal_label_textbox('1'))
        self.signals_dropdown_2 = self.findChild(QComboBox, 'SignalsComboBoxGraph2')
        for i in range(3):
            self.signals_dropdown_2.removeItem(0)
        # self.signals_dropdown_2.currentIndexChanged.connect(lambda:self.fill_signal_label_textbox('2'))
            
        # move button
        self.move_signal_button_1 = self.findChild(QPushButton, 'MoveToGraph2Button')
        self.move_signal_button_1.clicked.connect(lambda:self.move_signal('1'))
        self.move_signal_button_2 = self.findChild(QPushButton, 'MoveToGraph1Button')
        self.move_signal_button_2.clicked.connect(lambda:self.move_signal('2'))
        
        #signals renameing
        self.signals_naming_textbox_1 = self.findChild(QLineEdit, 'SignalTitleInputGraph1')
        self.signals_naming_textbox_1.textChanged.connect(lambda: self.change_signal_label('1'))
        self.signals_naming_textbox_2 = self.findChild(QLineEdit, 'SignalTitleInputGraph2')
        self.signals_naming_textbox_2.textChanged.connect(lambda: self.change_signal_label('2'))
        
    def fill_signal_label_textbox(self, viewer:str):
        if viewer == '1':
            if len(self.viewer1.channels):
                dropdown_index = self.signals_dropdown_1.currentIndex()
                current_label = self.viewer1.channels[dropdown_index].label
                self.signals_naming_textbox_1.setText(current_label)
        else:
            if len(self.viewer2.channels):
                dropdown_index = self.signals_dropdown_2.currentIndex()
                current_label = self.viewer2.channels[dropdown_index].label
                self.signals_naming_textbox_2.setText(current_label)
        
    def change_signal_label(self, viewer:str):
        if viewer == '1':
            if len(self.viewer1.channels):
                dropdown_index = self.signals_dropdown_1.currentIndex()
                new_label = self.signals_naming_textbox_1.text()
                self.viewer1.channels[dropdown_index].label = new_label
                self.refill_signals_dropdown('1')
        else:
            if len(self.viewer2.channels):
                new_label = self.signals_naming_textbox_2.text()
                dropdown_index = self.signals_dropdown_2.currentIndex()
                self.viewer2.channels[dropdown_index].label = new_label
                self.refill_signals_dropdown('2')
    
    def refill_signals_dropdown(self, viewer:str):
        if viewer == '1':
            self.signals_dropdown_1.clear()
            for signal in self.viewer1.channels:
                self.signals_dropdown_1.addItem(signal.label)
        else:
            self.signals_dropdown_2.clear()
            for signal in self.viewer2.channels:
                self.signals_dropdown_2.addItem(signal.label)
            
        
    def move_signal(self, from_viewer:str):
        if from_viewer == '1':
            dropdown_index = self.signals_dropdown_1.currentIndex()
            signal_y_data = self.viewer1.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer1.listDataItems()):
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    signal_to_be_removed = self.viewer1.channels[dropdown_index]
                    self.viewer1.remove_channel(signal_to_be_removed)
                    self.viewer1.removeItem(plot_item)
                    self.signals_dropdown_1.removeItem(dropdown_index)
                    self.viewer1.clear()
                    self.viewer1.plot_internal_signals()
                    self.viewer2.add_channel(signal_to_be_removed)
                    self.signals_dropdown_2.addItem(signal_to_be_removed.label)
                    self.viewer2.play()
                    self.viewer2.pause()
                    if len(self.viewer1.channels) == 0:
                        self.viewer1.pause()
                        self.PlayPauseButtonGraph1.setIcon(self.PlayImage)
                        
                    # self.viewer2.play()
                    # self.viewer2.pause()
                    break
        else:
            dropdown_index = self.signals_dropdown_2.currentIndex()
            signal_y_data = self.viewer2.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer2.listDataItems()):
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    signal_to_be_removed = self.viewer2.channels[dropdown_index]
                    self.viewer2.remove_channel(signal_to_be_removed)
                    self.viewer2.removeItem(plot_item)
                    self.signals_dropdown_2.removeItem(dropdown_index)
                    self.viewer2.clear()
                    self.viewer2.plot_internal_signals()
                    self.viewer1.add_channel(signal_to_be_removed)
                    self.signals_dropdown_1.addItem(signal_to_be_removed.label)
                    self.viewer1.play()
                    self.viewer1.pause()
                    if len(self.viewer2.channels) == 0:
                        self.viewer2.pause()
                        self.PlayPauseButtonGraph2.setIcon(self.PlayImage)
                    break


    def go_to_non_rectangle_signal_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'NonRectangleSignalPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)

    def go_to_home_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'MainPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)
            
    def go_to_gluing_page(self , data_x_viewer_1 , data_y_viewer_1 , data_x_viewer_2 , data_y_viewer_2):
        self.glued_viewer.clear()
        self.to_be_glued_signal_1 = CustomSignal(data_y_viewer_1)
        self.to_be_glued_signal_2 = CustomSignal(data_y_viewer_2)
        self.init_gluing_page(data_x_viewer_1 , data_x_viewer_2)
        if self.page_index != -1:
            self.Pages.setCurrentIndex(self.page_index)

    def init_gluing_page(self  ,data_x_viewer_1 , data_x_viewer_2):
        self.glued_viewer.add_glued_moving_channel(self.to_be_glued_signal_1, data_x_viewer_1)
        self.glued_viewer.add_glued_moving_channel(self.to_be_glued_signal_2, data_x_viewer_2)
        self.glued_signal_1_x_values = data_x_viewer_1
        self.glued_signal_2_x_values = data_x_viewer_2
        
                
    def set_gluing_scroll_bar_func(self):
        self.glued_viewer.clear()
        self.glued_viewer.remove_channel(self.to_be_glued_signal_2)
        self.glued_signal_2_x_values = [x + 100 for x in self.glued_signal_2_x_values]
        # self.glued_viewer.plot()
        
        
    def play_pause_graph1(self):
        if self.is_playing_graph1:
            self.PlayPauseButtonGraph1.setIcon(self.PauseImage)
            if len(self.viewer1.channels):
                self.viewer1.play()
        else:
            self.PlayPauseButtonGraph1.setIcon(self.PlayImage)
            # if len(self.viewer1.channels):
            self.viewer1.pause()
        self.is_playing_graph1 = not self.is_playing_graph1

    def play_pause_graph2(self):
        if self.is_playing_graph2:
            self.PlayPauseButtonGraph2.setIcon(self.PauseImage)
            if len(self.viewer2.channels):
                self.viewer2.play()
        else:
            self.PlayPauseButtonGraph2.setIcon(self.PlayImage)
            # if len(self.viewer2.channels):
            self.viewer2.pause()
        self.is_playing_graph2 = not self.is_playing_graph2

    def show_hide_graph1(self):
        if self.is_graph1_visible:
            self.ShowHideButtonGraph1.setIcon(self.ShowImage)
            
            dropdown_index = self.signals_dropdown_1.currentIndex()
            signal_y_data = self.viewer1.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer1.listDataItems()):
                # print(signal_y_data, plot_item.getData()[1])
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color='#000000'))
                    self.viewer1.channels[dropdown_index].visability = False
        else:
            self.ShowHideButtonGraph1.setIcon(self.HideImage)
            dropdown_index = self.signals_dropdown_1.currentIndex()
            signal_y_data = self.viewer1.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer1.listDataItems()):
                # print(signal_y_data, plot_item.getData()[1])
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color=self.viewer1.channels[dropdown_index].color))
                    self.viewer1.channels[dropdown_index].visability = True
        self.is_graph1_visible = not self.is_graph1_visible
    
    def show_hide_graph2(self):
        if self.is_graph2_visible:
            self.ShowHideButtonGraph2.setIcon(self.ShowImage)
            dropdown_index = self.signals_dropdown_2.currentIndex()
            signal_y_data = self.viewer2.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer2.listDataItems()):
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color='#000000'))
                    self.viewer2.channels[dropdown_index].visability = False
        else:
            self.ShowHideButtonGraph2.setIcon(self.HideImage)
            dropdown_index = self.signals_dropdown_2.currentIndex()
            signal_y_data = self.viewer2.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer2.listDataItems()):
                # print(signal_y_data, plot_item.getData()[1])
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color=self.viewer2.channels[dropdown_index].color))
                    self.viewer2.channels[dropdown_index].visability = True
        self.is_graph2_visible = not self.is_graph2_visible

    def change_color_graph1(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.change_plot_color('1', color.name())
            # print(color.name())
    
    def change_color_graph2(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.change_plot_color('2', color.name())
            # print(color.name())

    def gluing_mode(self):
        self.StartGluingButton.setEnabled(True)
        self.viewer1.show_glue_rectangle_func()
        self.viewer2.show_glue_rectangle_func()
    
    def start_gluing(self):
        selected_channel_index_viewer_1 = self.signals_dropdown_1.currentIndex()
        selected_channel_index_viewer_2 = self.signals_dropdown_2.currentIndex()
        [data_x_viewer_1 , data_y_viewer_1] = self.viewer1.process_region_coord(selected_channel_index_viewer_1)
        [data_x_viewer_2 , data_y_viewer_2] = self.viewer2.process_region_coord(selected_channel_index_viewer_2)
        self.go_to_gluing_page(data_x_viewer_1 , data_y_viewer_1 , data_x_viewer_2 , data_y_viewer_2)
        
    def update_gluing_interpolate(self):
        self.glued_viewer.clear()
        self.interpolation_order_combo_box = self.findChild(QComboBox , "comboBox_2")
        interpolation_order = self.interpolation_order_combo_box.currentIndex()
        self.gluer_interpolate = Gluer(self.to_be_glued_signal_1 , self.to_be_glued_signal_2 ,self.glued_signal_1_x_values , self.glued_signal_2_x_values )
        self.y_interpolated= self.gluer_interpolate.interpolate( interpolation_order)
        print(self.gluer_interpolate.signal_1_x_values[-1])
        print(self.gluer_interpolate.signal_2_x_values[0])
        if(self.gluer_interpolate.signal_1_x_values[0] < self.gluer_interpolate.signal_2_x_values[0] ):
            overlap_start = max(min(self.gluer_interpolate.signal_2_x_values) ,min(self.gluer_interpolate.signal_1_x_values))
            overlap_end = min(max(self.gluer_interpolate.signal_2_x_values) ,max(self.gluer_interpolate.signal_1_x_values))
            
            x_overlapped = np.linspace(overlap_start , overlap_end , num = 1000)
            
            signal_1_x_values_before_interpolated_part = self.gluer_interpolate.signal_1_x_values[:x_overlapped[0]]
            signal_2_x_values_before_interpolated_part = self.gluer_interpolate.signal_2_x_values[x_overlapped[-1]:]
            
            signal_1_y_values_before_interpolated_part = self.gluer_interpolate.signal_1_y_values[:self.y_interpolated[0]]
            signal_2_x_values_before_interpolated_part = self.gluer_interpolate.signal_2_x_values[x_overlapped[-1]:]
            
            glued_interpolated_overlapped_signal_x_values = np.concatenate([signal_1_x_values_before_interpolated_part , x_overlapped ,signal_2_x_values_before_interpolated_part])
            glued_interpolated_overlapped_signal_y_values = np.concatenate([self.to_be_glued_signal_1.signal , self.y_interpolated , self.to_be_glued_signal_2.signal])
            
            
        else:
            x_gap = np.linspace(self.gluer_interpolate.signal_1_x_values[-1] , self.gluer_interpolate.signal_2_x_values[0], num = 1000)
            glued_interpolated_gapped_signal_x_values = np.concatenate([self.glued_signal_1_x_values , x_gap ,self.glued_signal_2_x_values])
            glued_interpolated_gapped_signal_y_values = np.concatenate([self.to_be_glued_signal_1.signal , self.y_interpolated , self.to_be_glued_signal_2.signal])
            
            self.glued_viewer.plot(glued_interpolated_gapped_signal_x_values , glued_interpolated_gapped_signal_y_values)
    
    def move_signal_left(self):
        pass
    def load_signal(self,viewer_number:str):
        '''
        viewer_number: 1 or 2
        '''
        file_path, _ = QFileDialog.getOpenFileName(self,'Open CSV File', '', 'CSV Files (*.csv);;All Files (*)' )
        if file_path:
            if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    for i, col in enumerate(df.columns):
                        if viewer_number == '1':
                            signal = CustomSignal(label=f"{col}_signal_{self.number_of_viewer_1_signals}_1", signal=df[col].values )
                            self.signals_dropdown_1.addItem(signal.label)
                        else:
                            signal = CustomSignal(label=f"{col}_signal_{self.number_of_viewer_2_signals}_2", signal=df[col].values )
                            self.signals_dropdown_2.addItem(signal.label)
                    ## testing ##
                        # print(f"Column Name: {col}")
                        # print(df[col].values)
                        # print(type(df[col].values))
                    ## testing ##
                        if viewer_number == "1":
                            self.viewer1.clear()
                            self.viewer1.add_channel(signal)
                        else:
                            self.viewer2.clear()
                            self.viewer2.add_channel(signal)
                            
                    if viewer_number == "1":
                            self.number_of_viewer_1_signals+=1
                            self.play_pause_graph1()
                            # self.viewer1.pause()
                    else:
                            self.number_of_viewer_2_signals+=1
                            self.play_pause_graph2()
                            # self.viewer2.pause()
                    # print(len(self.viewer1.channels))
            else:
                self.show_error("the file extention must be a csv file")
        else:
            # self.show_error("no file is uploaded")
            pass
    
    def change_view_mode(self, index, viewer_number):
        if viewer_number == '1':
            if index == 0:
                self.viewer1.y_axis_scroll_bar_enabled = True
            else:
                self.viewer1.y_axis_scroll_bar_enabled = False
        else:
            if index == 0:
                self.viewer2.y_axis_scroll_bar_enabled = True
            else:
                self.viewer2.y_axis_scroll_bar_enabled = False
                
    def change_plot_color(self, viewer:str, color:str):
        if viewer == '1':
            dropdown_index = self.signals_dropdown_1.currentIndex()
            signal_y_data = self.viewer1.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer1.listDataItems()):
                # print(signal_y_data, plot_item.getData()[1])
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color=color))
                    self.viewer1.channels[dropdown_index].color = color
                    # print("color changed")
        else:
            dropdown_index = self.signals_dropdown_2.currentIndex()
            signal_y_data = self.viewer2.channels[dropdown_index].signal
            for i, plot_item in enumerate(self.viewer2.listDataItems()):
                # print(signal_y_data, plot_item.getData()[1])
                if np.array_equal(signal_y_data, plot_item.getData()[1]):
                    plot_item.setPen(pg.mkPen(color=color))
                    self.viewer1.channels[dropdown_index].color = color
                    
    def rewind_graph1(self):
        if self.is_rewinding_graph1:
            self.RewindButtonGraph1.setIcon(self.NoRewindImage)

        else:
            self.RewindButtonGraph1.setIcon(self.RewindImage)
        self.is_rewinding_graph1 = not self.is_rewinding_graph1

    def rewind_graph2(self):
        if self.is_rewinding_graph2:
            self.RewindButtonGraph2.setIcon(self.NoRewindImage)
        else:
            self.RewindButtonGraph2.setIcon(self.RewindImage)
        self.is_rewinding_graph2 = not self.is_rewinding_graph2
    
    def show_error(self, message:str):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("ERROR")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec_()

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())