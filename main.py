import subprocess
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())