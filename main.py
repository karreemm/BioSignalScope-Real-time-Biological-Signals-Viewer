import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QWidget, QColorDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon

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

        self.PlayImage = QIcon(':/Images/play.png')
        self.PauseImage = QIcon(':/Images/pause.png')
        self.HideImage = QIcon(':/Images/hide.png')
        self.ShowImage = QIcon(':/Images/show.png')

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

        data = ["25.4", "3.2", "120", "5.1", "30.9"]

        for column, value in enumerate(data):
            item = QtWidgets.QTableWidgetItem(value)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable) 
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)  
            self.tableWidget.setItem(0, column, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setVisible(False) 


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
        else:
            self.PlayPauseButtonGraph1.setIcon(self.PlayImage)
        self.is_playing_graph1 = not self.is_playing_graph1

    def play_pause_graph2(self):
        if self.is_playing_graph2:
            self.PlayPauseButtonGraph2.setIcon(self.PauseImage)
        else:
            self.PlayPauseButtonGraph2.setIcon(self.PlayImage)
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

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())