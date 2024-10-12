# real_time_window.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon

class realTimeWindow(QMainWindow):
    def __init__(self):
        super(realTimeWindow, self).__init__()
        loadUi('realTimeWindow.ui', self)

        self.setWindowIcon(QIcon('logo.png'))
        self.setWindowTitle('Real Time Window')

        min_height = 300
        min_width = 300

        max_height = 400
        max_width = 400

        self.setMinimumHeight(min_height)
        self.setMinimumWidth(min_width)

        self.setMaximumHeight(max_height)
        self.setMaximumWidth(max_width)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = realTimeWindow()
    window.show()
    sys.exit(app.exec_())