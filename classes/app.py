import sys
from spiderPlot import SpiderPlot
from spiderPlot import PlotControls
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from resampled_data import wave
from CSVLoader import CSVLoader  # The CSVLoader class we defined earlier

'''
We still need to:
    set labels (column names) to the vertices 
    make the movement smoother
    plot a time series data not just values
    some UI tools:
        upload file
        start
        stop
        time frame showed as a timer stopwatch
'''

if __name__ == "__main__":
    # Example usage
    app = QApplication(sys.argv)

    csv_loader = CSVLoader()

    dir_list = ['data1', 'data2']  # List of CSV files (without the .csv extension)
    target_sampling_rate = 10  # The desired sampling rate
    interpolation_order = 'linear'  # Interpolation method, could be 'linear', 'quadratic', etc.

    # Instantiate the wave class
    wave_instance = wave(dir_list, target_sampling_rate, interpolation_order)
        
    # Print the resampled data
    print(wave_instance.data_samples)

    # Create the main window and layout
    window = QWidget()
    layout = QVBoxLayout(window)

    # Create and adxxxxxxxxxxxx d the SpiderPlot widget
    graph = SpiderPlot(wave_instance.data_samples)
    layout.addWidget(graph)

    # Create and add the CSVLoader controls
    layout.addWidget(csv_loader.load_button)
    layout.addWidget(csv_loader.file_count_label)

    # Create and add the PlotControls widget
    graph_controls = PlotControls(graph)
    layout.addWidget(graph_controls)

    # Configure the main window
    window.setWindowTitle("Spider Plot")
    window.setGeometry(200, 200, 600, 800)
    window.setLayout(layout)

    # Show the main window
    window.show()

    # Start the application
    sys.exit(app.exec_())
