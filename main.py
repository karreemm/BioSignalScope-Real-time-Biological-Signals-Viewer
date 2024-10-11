import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton,QComboBox,  QMessageBox, QWidget, QColorDialog, QFrame, QVBoxLayout, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from classes.viewer import Viewer
from classes.channel_ import CustomSignal
import pandas as pd 

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

        self.GluingModeButton = self.findChild(QPushButton, 'GluingModeButton')
        self.GluingModeButton.clicked.connect(self.gluing_mode)

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
        self.change_view_mode(0, 1)
        self.view_modes_dropdown_2 = self.findChild(QComboBox, 'ModeComboBoxGraph2')
        self.view_modes_dropdown_2.currentIndexChanged.connect(lambda index : self.change_view_mode(index, '2'))
        self.change_view_mode(0, 2)
        
        # initializing the signals dropdown 
        self.signals_dropdown_1 = self.findChild(QComboBox, 'SignalsComboBoxGraph1')
        for i in range(3):
            self.signals_dropdown_1.removeItem(0)
        self.signals_dropdown_2 = self.findChild(QComboBox, 'SignalsComboBoxGraph2')
        for i in range(3):
            self.signals_dropdown_2.removeItem(0)
        


    def go_to_non_rectangle_signal_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'NonRectangleSignalPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)

    def go_to_home_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'MainPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)

    def play_pause_graph1(self):
        if self.is_playing_graph1:
            self.PlayPauseButtonGraph1.setIcon(self.PauseImage)
            if len(self.viewer1.channels):
                self.viewer1.play()
        else:
            self.PlayPauseButtonGraph1.setIcon(self.PlayImage)
            if len(self.viewer1.channels):
                self.viewer1.pause()
        self.is_playing_graph1 = not self.is_playing_graph1

    def play_pause_graph2(self):
        if self.is_playing_graph2:
            self.PlayPauseButtonGraph2.setIcon(self.PauseImage)
            if len(self.viewer2.channels):
                self.viewer2.play()
        else:
            self.PlayPauseButtonGraph2.setIcon(self.PlayImage)
            if len(self.viewer2.channels):
                self.viewer2.pause()
        self.is_playing_graph2 = not self.is_playing_graph2

    def show_hide_graph1(self):
        if self.is_graph1_visible:
            self.ShowHideButtonGraph1.setIcon(self.ShowImage)
        else:
            self.ShowHideButtonGraph1.setIcon(self.HideImage)
        self.is_graph1_visible = not self.is_graph1_visible
    
    def show_hide_graph2(self):
        if self.is_graph2_visible:
            self.ShowHideButtonGraph2.setIcon(self.ShowImage)
        else:
            self.ShowHideButtonGraph2.setIcon(self.HideImage)
        self.is_graph2_visible = not self.is_graph2_visible

    def change_color_graph1(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())
    
    def change_color_graph2(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())

    def gluing_mode(self):
        self.StartGluingButton.setEnabled(True)
        
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
                            signal = CustomSignal(label=f"{col}_signal_{self.number_of_viewer_1_signals}", signal=df[col].values )
                            self.signals_dropdown_1.addItem(signal.label)
                        else:
                            signal = CustomSignal(label=f"{i}_signal_{self.number_of_viewer_2_signals}", signal=df[col].values )
                            self.signals_dropdown_2.addItem(signal.label)
                    ## testing ##
                        print(f"Column Name: {col}")
                        print(df[col].values)
                        print(type(df[col].values))
                    ## testing ##
                        if viewer_number == "1":
                            self.viewer1.add_channel(signal)
                        else:
                            self.viewer2.add_channel(signal)
                            
                    if viewer_number == "1":
                            self.number_of_viewer_1_signals+=1
                    else:
                            self.number_of_viewer_2_signals+=1
                    print(len(self.viewer1.channels))
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