import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel

class CSVLoader(QWidget):
    def __init__(self, load_button):
        super().__init__()

        self.csv_files = []
        
        self.load_button =load_button
        self.load_button.clicked.connect(self.load_csv_files)
        
        
        
    def load_csv_files(self):
        """
        Open a file dialog to select CSV files and save the file paths to the list.
        """
        # Open the file dialog to select multiple CSV files
        files, _ = QFileDialog.getOpenFileNames(self, "Open CSV Files", "", "CSV Files (*.csv)")
        self.csv_files = []

        # If files are selected, store the file paths
        if files:
            self.csv_files.extend(files)
            

    
    def get_csv_files(self):
        """
        Return the list of CSV file paths.
        """
        return self.csv_files
