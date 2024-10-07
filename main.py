import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton, QWidget
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

        self.Pages = self.findChild(QStackedWidget, 'stackedWidget')  
        self.NonRectangleSignalButton = self.findChild(QPushButton, 'NonRectangleSignalButton')
        self.BackHomeButton = self.findChild(QPushButton, 'BackHomeButton')

        self.NonRectangleSignalButton.clicked.connect(self.go_to_non_rectangle_signal_page)
        self.BackHomeButton.clicked.connect(self.go_to_home_page)

        min_height = 700
        min_width = 1150

        self.setMinimumHeight(min_height)
        self.setMinimumWidth(min_width)

    def go_to_non_rectangle_signal_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'NonRectangleSignalPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)
        else:
            print("NonRectangleSignalPage not found in the stacked widget.")

    def go_to_home_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'MainPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)
        else:
            print("HomePage not found in the stacked widget.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
