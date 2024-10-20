import subprocess
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication,QSlider,  QMainWindow,QLineEdit,  QStackedWidget, QPushButton,QComboBox,  QMessageBox, QWidget, QColorDialog, QFrame, QVBoxLayout, QFileDialog ,QScrollBar, QHBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from classes.spiderPlot import SpiderPlot
from classes.resampled_data import wave
from classes.spiderPlot import PlotControls
from classes.viewer import Viewer
from classes.channel_ import CustomSignal
from classes.gluer import Gluer
import pandas as pd 
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image , Spacer , Paragraph , PageBreak
import copy
from PyQt5.QtCore import Qt
from feature_classes.realTimeSignal import RealTimeSignal
from feature_classes.navigations import Navigations
from helper_functions.compile_qrc import compile_qrc

compile_qrc()

import CompiledImages  

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi('main.ui', self)
        self.navigation = Navigations()
        self.RealTimeSignal = RealTimeSignal()
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
        self.RewindImage = QIcon(':/Images/rewindNew.png')
        self.NoRewindImage = QIcon(':/Images/noRewindNew.png')
        self.LinkImage = QIcon(':/Images/linkB.png')
        self.UnlinkImage = QIcon(':/Images/unlink.png')

        self.real_time_window = None

        self.is_rewinding_graph1 = False
        self.is_rewinding_graph2 = False

        self.is_playing_graph1 = False  
        self.is_playing_graph2 = False  

        self.is_graph1_visible = True
        self.is_graph2_visible = True

        self.is_linked = True

        self.Pages = self.findChild(QStackedWidget, 'stackedWidget') 
        self.MainPage = self.Pages.indexOf(self.findChild(QWidget , 'MainPage'))
        self.RealTimeSignalPage = self.Pages.indexOf(self.findChild(QWidget , 'RealTimePage'))
        self.NonRectangleSignalPage = self.Pages.indexOf(self.findChild(QWidget , 'NonRectangleSignalPage'))
        self.NonRectangleSignalButton = self.findChild(QPushButton, 'NonRectangleSignalButton')
        self.NonRectangleSignalButton.clicked.connect(self.go_to_non_rectangle_signal_page)

        self.NonRectangleGraphTimeSlider = self.findChild(QSlider, 'horizontalSlider')
        
        self.BackHomeButton1 = self.findChild(QPushButton, 'BackHomeButton1')
        self.BackHomeButton1.clicked.connect(self.navigation.go_to_home_page)

        # self.BackHomeButton2 = self.findChild(QPushButton, 'BackHomeButton2')
        # self.BackHomeButton2.clicked.connect(self.navigation.go_to_home_page)

        self.BackHomeButton3 = self.findChild(QPushButton, 'BackHomeButton3')
        self.BackHomeButton3.clicked.connect(self.go_to_home_page_from_real_time_signal)
        
        self.NonRectangleGraph = self.findChild(QFrame, 'NonRectangleGraph')
        
        self.UploadSignalNonRectangle= self.findChild(QPushButton, 'UploadSignalNonRectangle')
        self.UploadSignalNonRectangle.clicked.connect(self.draw_new_graph)

        target_sampling_rate = 10  # The desired sampling rate
        interpolation_order = 'linear'  # Interpolation method, could be 'linear', 'quadratic', etc.

        self.wave_instance = None
        self.horizontalLayout_15 = self.findChild(QHBoxLayout, 'horizontalLayout_15')
        
        
        self.PlayPauseNonRectangleButton = self.findChild(QPushButton, 'PlayPauseNonRectangleButton')
        
        self.ReplayNonRectangleButton = self.findChild(QPushButton, 'ReplayNonRectangleButton')

        self.SpeedSliderNonRectangleGraph = self.findChild(QSlider,'SpeedSliderNonRectangleGraph')
        
        self.BackButtonNonRectangle = self.findChild(QPushButton, 'BackButtonNonRectangle')
        
        self.NextButtonNonRectangle = self.findChild(QPushButton, 'NextButtonNonRectangle')
        
        self.ChangeColorButtonNonRectangle = self.findChild(QPushButton, 'ChangeColorButtonNonRectangle')
        
        self.graph = None
        self.spider_viewer_control = None
        
        
        self.NonRectangleSignalButton = self.findChild(QPushButton, 'NonRectangleSignalButton')
        self.NonRectangleSignalButton.clicked.connect(self.navigation.go_to_non_rectangle_signal_page)

        # self.BackHomeButton1 = self.findChild(QPushButton, 'BackHomeButton1')
        # self.BackHomeButton1.clicked.connect(self.navigation.go_to_home_page)

        self.BackHomeButton2 = self.findChild(QPushButton, 'BackHomeButton2')
        self.BackHomeButton2.clicked.connect(self.go_to_home_page_from_gluing)

        # self.BackHomeButton3 = self.findChild(QPushButton, 'BackHomeButton3')
        # self.BackHomeButton3.clicked.connect(self.navigation.go_to_home_page)
        
        # self.RealTimeViewSignalButton.clicked.connect(self.RealTimeSignal.show_real_time_graph)
        # self.RealTimeViewSignalButton.clicked.connect(self.RealTimeSignal.disable_view_button)

        self.RealTimeSignalInput = self.findChild(QLineEdit , "RealTimeSignalInput")
        self.RealTimeSignalInput.textChanged.connect(self.RealTimeSignal.validate_api_link)
        
        self.PlayPauseButtonRealTime = self.findChild(QPushButton , "PlayPauseButtonRealTime")
        self.PlayPauseButtonRealTime.clicked.connect(self.RealTimeSignal.toggle_play_pause_real_time)
        
        self.RealTimeScroll = self.findChild(QScrollBar , "RealTimeScroll")
        self.RealTimeScroll.setOrientation(Qt.Horizontal)
        self.RealTimeScroll.valueChanged.connect(self.RealTimeSignal.scroll_graph)

        self.graphWidget = pg.PlotWidget()
        self.layout = QtWidgets.QVBoxLayout(self.RealTimeSignalFrame)
        self.layout.addWidget(self.graphWidget)
        
        
        self.navigation.initialize(self.NonRectangleSignalButton, self.BackHomeButton1, self.BackHomeButton2, self.BackHomeButton3, self.RealTimeSignalButton, self.RealTimeSignalPage, self.MainPage, self.NonRectangleSignalPage, self.Pages)
        self.RealTimeSignal.initialize(self.RealTimeSignalInput  , self.PlayPauseButtonRealTime , self.RealTimeScroll, self.graphWidget , self.Pages , self.RealTimeSignalPage)

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

        self.isGlueRegionShowing = False
        
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
        
        self.MoveSignalRightButton = self.findChild(QPushButton , "pushButton")
        self.MoveSignalRightButton.clicked.connect(self.move_signal_right)

        self.LinkGraphsButton = self.findChild(QPushButton, 'LinkGraphsButton')
        self.LinkGraphsButton.clicked.connect(self.link_graphs)
        # self.LinkGraphsButton.setIcon(self.LinkImage)
        
        self.AddToPDFReport = self.findChild(QPushButton ,"AddToReportButton")
        self.AddToPDFReport.clicked.connect(self.add_to_pdf_report)
        self.captured_report_images_counter = 1
        self.captured_report_images_filenames = []
        self.captured_report_images_statistics = []
        
        self.GeneratePDFReport = self.findChild(QPushButton , "GeneratePDFButton")
        self.GeneratePDFReport.clicked.connect(self.generate_pdf_report)

        self.interpolation_order_combo_box = self.findChild(QComboBox , "comboBox_2")
        self.interpolation_order_combo_box.activated.connect(self.update_gluing_interpolate)

        self.RealTimeSignalButton = self.findChild(QPushButton, 'RealTimeSignalButton')
        self.RealTimeSignalButton.clicked.connect(self.RealTimeSignal.go_to_real_time_page)
        
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
        
        self.stats_data = ["null", "null", "null", "null", "null"]

        for column, value in enumerate(self.stats_data):
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
        self.viewer1.sigRangeChanged.connect(lambda:self.change_graph_play_pause_icon_for_rewinding('1'))
        
        self.viewer_frame2 = self.findChild(QFrame, 'Graph2Frame')
        self.frame2_layout = QVBoxLayout()
        self.viewer2 = Viewer()
        self.frame2_layout.addWidget(self.viewer2)
        self.viewer_frame2.setLayout(self.frame2_layout)
        self.play_pause_graph2()
        self.viewer2.sigRangeChanged.connect(lambda:self.change_graph_play_pause_icon_for_rewinding('2'))
        
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
        # self.change_view_mode(1, '1')
        self.view_modes_dropdown_1.setCurrentIndex(1)
        self.view_modes_dropdown_2 = self.findChild(QComboBox, 'ModeComboBoxGraph2')
        self.view_modes_dropdown_2.currentIndexChanged.connect(lambda index : self.change_view_mode(index, '2'))
        # self.change_view_mode(1, '2')
        self.view_modes_dropdown_2.setCurrentIndex(1)
        
        # Viewer 1 Scroll bars Initialization
        self.scrolling_x_axis_scrollbar_viewer1 = self.findChild(QScrollBar , "HorizontalScrollGraph1")
        self.scrolling_x_axis_scrollbar_viewer1.valueChanged.connect(lambda: self.viewer1.scrolling_x_axis_scrollbar_effect(self.scrolling_x_axis_scrollbar_viewer1.value()))
        
        self.scrolling_y_axis_scrollbar_viewer1 = self.findChild(QScrollBar , "VerticalScrollGraph1")
        self.viewer1.viewBox.sigRangeChanged.connect(self.set_viewer1_sliders_value)
        self.scrolling_y_axis_scrollbar_viewer1.valueChanged.connect(lambda: self.viewer1.scrolling_y_axis_scrollbar_effect(self.scrolling_y_axis_scrollbar_viewer1.value()))
        
        
        # Viewer 2 Scroll bars Initialization
        self.scrolling_x_axis_scrollbar_viewer2 = self.findChild(QScrollBar , "HorizontalScrollGraph2")
        self.scrolling_x_axis_scrollbar_viewer2.valueChanged.connect(lambda: self.viewer2.scrolling_x_axis_scrollbar_effect(self.scrolling_x_axis_scrollbar_viewer2.value()))
        
        self.scrolling_y_axis_scrollbar_viewer2 = self.findChild(QScrollBar , "VerticalScrollGraph2")
        self.viewer2.viewBox.sigRangeChanged.connect(self.set_viewer2_sliders_value)
        self.scrolling_y_axis_scrollbar_viewer2.valueChanged.connect(lambda: self.viewer2.scrolling_y_axis_scrollbar_effect(self.scrolling_y_axis_scrollbar_viewer2.value()))
        
        
        
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
        
        # speed assignment 
        self.signal_speed_slider_1 = self.findChild(QSlider, 'SpeedSliderGraph1')
        self.signal_speed_slider_1.setRange(0,4)
        self.signal_speed_slider_1.setTickInterval(1)
        self.signal_speed_slider_1.valueChanged.connect(lambda value: self.on_slider_value_changed(value, '1'))
        self.signal_speed_slider_2 = self.findChild(QSlider, 'SpeedSliderGraph2')
        self.signal_speed_slider_2.setRange(0,4)
        self.signal_speed_slider_2.setTickInterval(1)
        self.signal_speed_slider_2.valueChanged.connect(lambda value: self.on_slider_value_changed(value, '2'))
        
        # replay button
        self.replay_button_1 = self.findChild(QPushButton, 'ReplayButtonGraph1')
        self.replay_button_1.clicked.connect(lambda:self.replay_signal('1'))
        self.replay_button_2 = self.findChild(QPushButton, 'ReplayButtonGraph2')
        self.replay_button_2.clicked.connect(lambda:self.replay_signal('2'))
        
    def draw_new_graph(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open CSV Files", "", "CSV Files (*.csv)")
        csv_files = []
        # If files are selected, store the file paths
        if files:
            csv_files.extend(files)
            self.wave_instance = wave(files_directories = csv_files)
            print(f'CSV files:{csv_files}'  )
            self.horizontalLayout_15.removeWidget(self.graph)

            self.graph = SpiderPlot(self.wave_instance.data_samples, self.NonRectangleGraphTimeSlider)    
            self.spider_viewer_control = PlotControls(self.PlayImage, self.PauseImage ,self.graph, self.BackButtonNonRectangle, self.NextButtonNonRectangle, 
                                                self.SpeedSliderNonRectangleGraph, self.PlayPauseNonRectangleButton, self.ReplayNonRectangleButton, self.ChangeColorButtonNonRectangle,self.NonRectangleGraphTimeSlider)
            self.horizontalLayout_15.addWidget(self.graph)
        
        # linking button 
        
    def replay_signal(self, viewer:str):
        if viewer == '1':
            if not self.is_playing_graph1:
                self.viewer1.replay()
                self.is_playing_graph1 = True 
            else:
                print("condition 2")
                self.play_pause_graph1()
                self.viewer1.replay()
        else:
            if not self.is_playing_graph2:
                self.is_playing_graph2 = True 
                self.viewer2.replay()
            else:
                print("condition 2")
                self.play_pause_graph2()
                self.viewer2.replay()
        
    def on_slider_value_changed(self,value, viewer:str):
        speeds = [70,60,50,40,30]
        new_speed = speeds[value]
        if viewer == '1':
            self.play_pause_graph1()
            self.viewer1.cine_speed(new_speed)
            self.play_pause_graph1()
        else:
            self.play_pause_graph2()
            self.viewer2.cine_speed(new_speed)
            self.play_pause_graph2()
        
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
                    scrolling_x_axis_scrollbar_viewer2_page_step = 1075
                    self.scrolling_x_axis_scrollbar_viewer2.setMaximum(int(self.viewer2.x_axis[-1] - scrolling_x_axis_scrollbar_viewer2_page_step))
                    self.scrolling_y_axis_scrollbar_viewer2.setMinimum(int(self.viewer2.min_signals_value))
                    self.scrolling_y_axis_scrollbar_viewer2.setPageStep(int(self.viewer2.viewBox.viewRange()[1][1] - self.viewer2.viewBox.viewRange()[1][0]))
                    scrolling_y_axis_scrollbar_viewer2_page_step = 325
                    self.scrolling_y_axis_scrollbar_viewer2.setMaximum(int(self.viewer2.max_signals_value + int(self.viewer2.viewBox.viewRange()[1][1] - self.viewer2.viewBox.viewRange()[1][0]) - scrolling_y_axis_scrollbar_viewer2_page_step))
                    self.viewer1.update_x_axis()
                    if self.viewer1.x_axis[-1] < self.viewer1.viewRange()[0][1]:
                        self.replay_signal('1')
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
                    scrolling_x_axis_scrollbar_viewer1_page_step = 1075
                    self.scrolling_x_axis_scrollbar_viewer1.setMaximum(int(self.viewer1.x_axis[-1] - scrolling_x_axis_scrollbar_viewer1_page_step))
                    self.scrolling_y_axis_scrollbar_viewer1.setMinimum(int(self.viewer1.min_signals_value))
                    self.scrolling_y_axis_scrollbar_viewer1.setPageStep(int(self.viewer1.viewBox.viewRange()[1][1] - self.viewer1.viewBox.viewRange()[1][0]))
                    scrolling_y_axis_scrollbar_viewer1_page_step = 325
                    self.scrolling_y_axis_scrollbar_viewer1.setMaximum(int(self.viewer1.max_signals_value + int(self.viewer1.viewBox.viewRange()[1][1] - self.viewer1.viewBox.viewRange()[1][0]) - scrolling_y_axis_scrollbar_viewer1_page_step))
                    self.viewer2.update_x_axis()
                    if self.viewer2.x_axis[-1] < self.viewer2.viewRange()[0][1]:
                        self.replay_signal('2')
                    break


    def go_to_non_rectangle_signal_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'NonRectangleSignalPage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)

            
    def go_to_home_page_from_gluing(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'MainPage'))
        self.viewer1.removeItem(self.viewer1.gluing_selected_region)
        self.viewer2.removeItem(self.viewer2.gluing_selected_region)
        self.isGlueRegionShowing = False
        self.StartGluingButton.setEnabled(False)
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)
            
    def go_to_home_page_from_real_time_signal(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'MainPage'))
        self.RealTimeSignal.timer.stop()
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
        self.update_gluing_interpolate()
        
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
        if(not self.isGlueRegionShowing):
            self.StartGluingButton.setEnabled(True)
            self.viewer1.show_glue_rectangle_func()
            self.viewer2.show_glue_rectangle_func()
        else:
            self.StartGluingButton.setEnabled(False)
            self.viewer1.removeItem(self.viewer1.gluing_selected_region)
            self.viewer2.removeItem(self.viewer2.gluing_selected_region)
        self.isGlueRegionShowing = not self.isGlueRegionShowing
    def start_gluing(self):
        selected_channel_index_viewer_1 = self.signals_dropdown_1.currentIndex()
        selected_channel_index_viewer_2 = self.signals_dropdown_2.currentIndex()
        [data_x_viewer_1 , data_y_viewer_1] = self.viewer1.process_region_coord(selected_channel_index_viewer_1)
        [data_x_viewer_2 , data_y_viewer_2] = self.viewer2.process_region_coord(selected_channel_index_viewer_2)
        self.go_to_gluing_page(data_x_viewer_1 , data_y_viewer_1 , data_x_viewer_2 , data_y_viewer_2)
        
    def update_gluing_interpolate(self):
        self.glued_viewer.clear()
        interpolation_order = self.interpolation_order_combo_box.currentIndex()
        self.gluer_interpolate = Gluer(self.to_be_glued_signal_1 , self.to_be_glued_signal_2 ,self.glued_signal_1_x_values , self.glued_signal_2_x_values )
        self.y_interpolated= self.gluer_interpolate.interpolate( interpolation_order)
        if(self.gluer_interpolate.signal_2_x_values[0] < self.gluer_interpolate.signal_1_x_values[0]):  ## Signal 2 is the first signal in timeline
            if(self.gluer_interpolate.signal_1_x_values[0] < self.gluer_interpolate.signal_2_x_values[-1]):
                overlap_start = max(min(self.gluer_interpolate.signal_2_x_values) ,min(self.gluer_interpolate.signal_1_x_values))
                overlap_end = min(max(self.gluer_interpolate.signal_2_x_values) ,max(self.gluer_interpolate.signal_1_x_values))
                
                x_overlapped = np.linspace(int(overlap_start) , int(overlap_end) , num= np.int16(overlap_end) - np.int16(overlap_start))
                x_overlapped = [int(x) for x in x_overlapped]
                signal_1_x_values_as_int = [int(x) for x in self.gluer_interpolate.signal_1_x_values]
                signal_2_x_values_as_int = [int(x) for x in self.gluer_interpolate.signal_2_x_values]
                
                x_overlapped_first_value_index_in_signal_2 = signal_2_x_values_as_int.index(int(x_overlapped[0]))
                x_overlapped_last_value_index_in_signal_1 = signal_1_x_values_as_int.index(int(x_overlapped[-1]))
                
                signal_2_x_values_before_interpolated_part = self.gluer_interpolate.signal_2_x_values[:x_overlapped_first_value_index_in_signal_2]
                signal_1_x_values_after_interpolated_part = self.gluer_interpolate.signal_1_x_values[x_overlapped_last_value_index_in_signal_1:]
                
                # signal_2_x_values_before_interpolated_part_as_int = [int(x) for x in signal_2_x_values_before_interpolated_part]
                # signal_1_x_values_after_interpolated_part_as_int = [int(x) for x in signal_1_x_values_after_interpolated_part]
                
                signal_2_y_values_before_interpolated_part = self.gluer_interpolate.signal_2.signal[:x_overlapped_first_value_index_in_signal_2]
                signal_1_y_values_after_interpolated_part = self.gluer_interpolate.signal_1.signal[x_overlapped_last_value_index_in_signal_1:]
                
                self.glued_interpolated_overlapped_signal_x_values = np.concatenate([signal_2_x_values_before_interpolated_part , x_overlapped ,signal_1_x_values_after_interpolated_part])
                self.glued_interpolated_overlapped_signal_y_values = np.concatenate([signal_2_y_values_before_interpolated_part , self.y_interpolated , signal_1_y_values_after_interpolated_part])
                
                x_overlapped.insert(0 , signal_2_x_values_before_interpolated_part[-1])
                x_overlapped.append(signal_1_x_values_after_interpolated_part[0])
                self.y_interpolated = list(self.y_interpolated)
                self.y_interpolated.append(signal_1_y_values_after_interpolated_part[0])
                self.y_interpolated.insert(0, signal_2_y_values_before_interpolated_part[-1])
                
                self.glued_viewer.plot(signal_2_x_values_before_interpolated_part , signal_2_y_values_before_interpolated_part , pen = pg.mkPen(color = 'red'))
                self.glued_viewer.plot(x_overlapped , self.y_interpolated , pen = pg.mkPen(color = 'blue'))
                self.glued_viewer.plot(signal_1_x_values_after_interpolated_part ,signal_1_y_values_after_interpolated_part , pen = pg.mkPen(color = 'red'))
                self.gluer_interpolate.get_statistics(self.glued_interpolated_overlapped_signal_x_values ,self.glued_interpolated_overlapped_signal_y_values )
                self.update_statistics()
                
            else:
                x_gap = np.linspace(self.gluer_interpolate.signal_2_x_values[-1] , self.gluer_interpolate.signal_1_x_values[0], num = np.int16(self.gluer_interpolate.signal_1_x_values[0]) - np.int16(self.gluer_interpolate.signal_2_x_values[-1]))
                self.glued_interpolated_gapped_signal_x_values = np.concatenate([self.glued_signal_2_x_values , x_gap ,self.glued_signal_1_x_values])
                self.glued_interpolated_gapped_signal_y_values = np.concatenate([self.to_be_glued_signal_2.signal , self.y_interpolated , self.to_be_glued_signal_1.signal])
                
                x_gap = list(x_gap)
                x_gap.insert(0 , self.glued_signal_2_x_values[-1])
                x_gap.append(self.glued_signal_1_x_values[0])
                self.y_interpolated = list(self.y_interpolated)
                self.y_interpolated.append(self.to_be_glued_signal_1.signal[0])
                self.y_interpolated.insert(0, self.to_be_glued_signal_2.signal[-1])
                
                self.glued_viewer.plot(self.glued_signal_2_x_values , self.to_be_glued_signal_2.signal , pen = pg.mkPen(color = 'red'))
                self.glued_viewer.plot(x_gap , self.y_interpolated , pen = pg.mkPen(color = 'blue'))
                self.glued_viewer.plot(self.glued_signal_1_x_values , self.to_be_glued_signal_1.signal , pen = pg.mkPen(color = 'red'))
                self.gluer_interpolate.get_statistics(self.glued_interpolated_gapped_signal_x_values ,self.glued_interpolated_gapped_signal_y_values )
                self.update_statistics()
                
        else:  #Signal 1 is the first signal in the timeline
            if(self.gluer_interpolate.signal_1_x_values[-1] > self.gluer_interpolate.signal_2_x_values[0]):
                overlap_start = max(min(self.gluer_interpolate.signal_2_x_values) ,min(self.gluer_interpolate.signal_1_x_values))
                overlap_end = min(max(self.gluer_interpolate.signal_2_x_values) ,max(self.gluer_interpolate.signal_1_x_values))
                
                x_overlapped = np.linspace(int(overlap_start) , int(overlap_end) , num= np.int16(overlap_end) - np.int16(overlap_start))
                x_overlapped = [int(x) for x in x_overlapped]
                signal_1_x_values_as_int = [int(x) for x in self.gluer_interpolate.signal_1_x_values]
                signal_2_x_values_as_int = [int(x) for x in self.gluer_interpolate.signal_2_x_values]
                x_overlapped_first_value_index_in_signal_1 = signal_1_x_values_as_int.index(int(x_overlapped[0]))
                x_overlapped_last_value_index_in_signal_2 = signal_2_x_values_as_int.index(int(x_overlapped[-1]))

                signal_1_x_values_before_interpolated_part = self.gluer_interpolate.signal_1_x_values[:x_overlapped_first_value_index_in_signal_1]
                signal_2_x_values_after_interpolated_part = signal_2_x_values_as_int[x_overlapped_last_value_index_in_signal_2:]
            
                signal_1_y_values_before_interpolated_part = self.gluer_interpolate.signal_1.signal[:x_overlapped_first_value_index_in_signal_1]
                signal_2_y_values_after_interpolated_part = self.gluer_interpolate.signal_2.signal[x_overlapped_last_value_index_in_signal_2 : ]
                
                self.glued_interpolated_overlapped_signal_x_values = np.concatenate([signal_1_x_values_before_interpolated_part , x_overlapped ,signal_2_x_values_after_interpolated_part])
                self.glued_interpolated_overlapped_signal_y_values = np.concatenate([signal_1_y_values_before_interpolated_part , self.y_interpolated , signal_2_y_values_after_interpolated_part])
                
                
                x_overlapped.insert(0 , signal_1_x_values_before_interpolated_part[-1])
                x_overlapped.append(signal_2_x_values_after_interpolated_part[0])
                self.y_interpolated = list(self.y_interpolated)
                self.y_interpolated.insert(0, signal_1_y_values_before_interpolated_part[-1])
                self.y_interpolated.append(signal_2_y_values_after_interpolated_part[0])
                
                self.glued_viewer.plot(signal_1_x_values_before_interpolated_part , signal_1_y_values_before_interpolated_part , pen = pg.mkPen(color = 'red'))
                self.glued_viewer.plot(x_overlapped , self.y_interpolated , pen = pg.mkPen(color = 'blue'))
                self.glued_viewer.plot(signal_2_x_values_after_interpolated_part , signal_2_y_values_after_interpolated_part , pen = pg.mkPen(color = 'red'))
                self.gluer_interpolate.get_statistics(self.glued_interpolated_overlapped_signal_x_values ,self.glued_interpolated_overlapped_signal_y_values )
                self.update_statistics()

            else:
                x_gap = np.linspace(self.gluer_interpolate.signal_1_x_values[-1] , self.gluer_interpolate.signal_2_x_values[0], num = np.int16(self.gluer_interpolate.signal_2_x_values[0]) - np.int16(self.gluer_interpolate.signal_1_x_values[-1]))
                self.glued_interpolated_gapped_signal_x_values = np.concatenate([self.glued_signal_1_x_values , x_gap ,self.glued_signal_2_x_values])
                self.glued_interpolated_gapped_signal_y_values = np.concatenate([self.to_be_glued_signal_1.signal , self.y_interpolated , self.to_be_glued_signal_2.signal])
                
                x_gap = list(x_gap)
                x_gap.insert(0 , self.glued_signal_1_x_values[-1])
                x_gap.append(self.glued_signal_2_x_values[0])
                self.y_interpolated = list(self.y_interpolated)
                self.y_interpolated.insert(0,  self.to_be_glued_signal_1.signal[-1])
                self.y_interpolated.append(self.to_be_glued_signal_2.signal[0])
                
                self.glued_viewer.plot(self.glued_signal_1_x_values , self.to_be_glued_signal_1.signal , pen = pg.mkPen(color = 'red'))
                self.glued_viewer.plot(x_gap , self.y_interpolated , pen = pg.mkPen(color = 'blue'))
                self.glued_viewer.plot(self.glued_signal_2_x_values , self.to_be_glued_signal_2.signal , pen = pg.mkPen(color = 'red'))
                self.gluer_interpolate.get_statistics(self.glued_interpolated_gapped_signal_x_values ,self.glued_interpolated_gapped_signal_y_values )
                self.update_statistics()
                
    def update_statistics(self ):
        self.stats_data[0] = self.gluer_interpolate.mean
        self.stats_data[1] = self.gluer_interpolate.std
        self.stats_data[2] = self.gluer_interpolate.duration
        self.stats_data[3] = self.gluer_interpolate.min
        self.stats_data[4] = self.gluer_interpolate.max
        for column, value in enumerate(self.stats_data):
            item = QtWidgets.QTableWidgetItem(value)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable) 
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)  
            self.tableWidget.setItem(0, column, item)
    
    def add_to_pdf_report(self):
        captured_data_region_exported_image = pyqtgraph.exporters.ImageExporter(self.glued_viewer.getPlotItem())
        captured_data_region_exported_image.parameters()['width'] = 3950  
        captured_data_region_exported_image.parameters()['height'] = 1000  
        captured_data_region_exported_image.export(f"./captured_report_signals/captured_region{self.captured_report_images_counter}.png")
        self.captured_report_images_filenames.append(f"./captured_report_signals/captured_region{self.captured_report_images_counter}.png")
        self.captured_report_images_counter += 1
        print(self.stats_data)
        current_stats_data = copy.copy(self.stats_data)
        self.captured_report_images_statistics.append(current_stats_data)  
        print(self.captured_report_images_statistics)  
        
    def generate_pdf_report(self):
        doc = SimpleDocTemplate("report.pdf", pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("Team 6", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        centered_style = styles['Heading2']
        centered_style.alignment = 1
        for i, (image_filename, stats) in enumerate(zip(self.captured_report_images_filenames, self.captured_report_images_statistics)):
            signal_title = Paragraph(f"Signal {i + 1}", centered_style)
            elements.append(signal_title)
            elements.append(Spacer(1, 20))

            img = Image(image_filename, width=612, height=310)
            elements.append(img)
            elements.append(Spacer(1, 20))

            data = [
                ['Mean', 'Std Dev', 'Duration', 'Min', 'Max'],
                [f"{float(stats[0]):.2f}", f"{float(stats[1]):.2f}", f"{float(stats[2]):.2f}", f"{float(stats[3]):.2f}", f"{float(stats[4]):.2f}"]
            ]

            table = Table(data, colWidths=[80, 80, 80, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)

            if i < len(self.captured_report_images_filenames) - 1:
                elements.append(PageBreak())

        doc.build(elements)
        self.captured_report_images_filenames.clear()
        self.captured_report_images_statistics.clear()
            
    def move_signal_left(self):
        self.glued_viewer.clear()
        self.glued_signal_2_x_values = [x - 50 for x in self.glued_signal_2_x_values ]
        self.init_gluing_page(self.glued_signal_1_x_values, self.glued_signal_2_x_values)
    
    def move_signal_right(self):
        self.glued_viewer.clear()
        self.glued_signal_2_x_values = [x + 50 for x in self.glued_signal_2_x_values ]
        self.init_gluing_page(self.glued_signal_1_x_values, self.glued_signal_2_x_values)
    
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
                            signal = CustomSignal(label=f"Untitled_{self.number_of_viewer_1_signals}_signal_1", signal=df[col].values )
                            self.signals_dropdown_1.addItem(signal.label)
                        else:
                            signal = CustomSignal(label=f"Untitled_{self.number_of_viewer_2_signals}_signal_2", signal=df[col].values )
                            self.signals_dropdown_2.addItem(signal.label)
                    ## testing ##
                        # print(f"Column Name: {col}")
                        # print(df[col].values)
                        # print(type(df[col].values))
                    ## testing ##
                        if viewer_number == "1":
                            self.viewer1.clear()
                            self.viewer1.add_channel(signal)
                            scrolling_x_axis_scrollbar_viewer1_page_step = 1075
                            self.scrolling_x_axis_scrollbar_viewer1.setMaximum(int(self.viewer1.x_axis[-1] - scrolling_x_axis_scrollbar_viewer1_page_step))
                            self.scrolling_y_axis_scrollbar_viewer1.setMinimum(int(self.viewer1.min_signals_value))
                            self.scrolling_y_axis_scrollbar_viewer1.setPageStep(int(self.viewer1.viewBox.viewRange()[1][1] - self.viewer1.viewBox.viewRange()[1][0]))
                            scrolling_y_axis_scrollbar_viewer1_page_step = 325
                            self.scrolling_y_axis_scrollbar_viewer1.setMaximum(int(self.viewer1.max_signals_value + int(self.viewer1.viewBox.viewRange()[1][1] - self.viewer1.viewBox.viewRange()[1][0]) - scrolling_y_axis_scrollbar_viewer1_page_step))
                            
                        else:
                            self.viewer2.clear()
                            self.viewer2.add_channel(signal)
                            scrolling_x_axis_scrollbar_viewer2_page_step = 1075
                            self.scrolling_x_axis_scrollbar_viewer2.setMaximum(int(self.viewer2.x_axis[-1] - scrolling_x_axis_scrollbar_viewer2_page_step))
                            self.scrolling_y_axis_scrollbar_viewer2.setMinimum(int(self.viewer2.min_signals_value))
                            self.scrolling_y_axis_scrollbar_viewer2.setPageStep(int(self.viewer2.viewBox.viewRange()[1][1] - self.viewer2.viewBox.viewRange()[1][0]))
                            scrolling_y_axis_scrollbar_viewer2_page_step = 325
                            self.scrolling_y_axis_scrollbar_viewer2.setMaximum(int(self.viewer2.max_signals_value + int(self.viewer2.viewBox.viewRange()[1][1] - self.viewer2.viewBox.viewRange()[1][0]) - scrolling_y_axis_scrollbar_viewer2_page_step))
                            
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
    
    def set_viewer1_sliders_value(self , view,ranges):
        x_axis_slider_value = ranges[0][0]
        y_axis_slider_value = ranges[1][0]
        self.scrolling_x_axis_scrollbar_viewer1.blockSignals(True)
        self.scrolling_x_axis_scrollbar_viewer1.setValue(int(x_axis_slider_value))
        self.scrolling_x_axis_scrollbar_viewer1.blockSignals(False)
        
        if self.viewer1.y_axis_scroll_bar_enabled :
            if not self.viewer1.scrolling_in_y_axis:
                self.scrolling_y_axis_scrollbar_viewer1.setEnabled(True)
                self.viewer1.viewBox.setMouseEnabled(x = True, y =True)
                self.viewer1.viewBox.enableAutoRange(x=False, y=False)
                self.viewer1.viewBox.setAutoVisible(x=False, y=False)
                self.scrolling_y_axis_scrollbar_viewer1.blockSignals(True)
                self.scrolling_y_axis_scrollbar_viewer1.setValue(int(y_axis_slider_value))
                
                self.scrolling_y_axis_scrollbar_viewer1.blockSignals(False)
        else:
            self.scrolling_y_axis_scrollbar_viewer1.setDisabled(True)
            self.viewer1.viewBox.setMouseEnabled(x = True, y =False)
            self.viewer1.viewBox.enableAutoRange(x=False, y=True)
            self.viewer1.viewBox.setAutoVisible(x=False, y=True)
            
    def set_viewer2_sliders_value(self , view,ranges):
        x_axis_slider_value = ranges[0][0]
        y_axis_slider_value = ranges[1][0]
        self.scrolling_x_axis_scrollbar_viewer2.blockSignals(True)
        self.scrolling_x_axis_scrollbar_viewer2.setValue(int(x_axis_slider_value))
        self.scrolling_x_axis_scrollbar_viewer2.blockSignals(False)
        
        if self.viewer2.y_axis_scroll_bar_enabled :
            if not self.viewer2.scrolling_in_y_axis:
                self.scrolling_y_axis_scrollbar_viewer2.setEnabled(True)
                self.viewer2.viewBox.setMouseEnabled(x = True, y =True)
                self.viewer2.viewBox.enableAutoRange(x=False, y=False)
                self.viewer2.viewBox.setAutoVisible(x=False, y=False)
                self.scrolling_y_axis_scrollbar_viewer2.blockSignals(True)
                self.scrolling_y_axis_scrollbar_viewer2.setValue(int(y_axis_slider_value))
                
                self.scrolling_y_axis_scrollbar_viewer2.blockSignals(False)
        else:
            self.scrolling_y_axis_scrollbar_viewer2.setDisabled(True)
            self.viewer2.viewBox.setMouseEnabled(x = True, y =False)
            self.viewer2.viewBox.enableAutoRange(x=False, y=True)
            self.viewer2.viewBox.setAutoVisible(x=False, y=True)
    
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
                    self.viewer2.channels[dropdown_index].color = color
                    
    def rewind_graph1(self):
        if self.is_rewinding_graph1:
            self.RewindButtonGraph1.setIcon(self.NoRewindImage)
            self.viewer1.rewind_state = False
        else:
            self.RewindButtonGraph1.setIcon(self.RewindImage)
            self.viewer1.rewind_state = True
        self.is_rewinding_graph1 = not self.is_rewinding_graph1

    def rewind_graph2(self):
        if self.is_rewinding_graph2:
            self.RewindButtonGraph2.setIcon(self.NoRewindImage)
            self.viewer2.rewind_state = False
        else:
            self.RewindButtonGraph2.setIcon(self.RewindImage)
            self.viewer2.rewind_state = True
        self.is_rewinding_graph2 = not self.is_rewinding_graph2
        
    def change_graph_play_pause_icon_for_rewinding(self, viewer:str):
        if viewer == '1':
            if not self.is_rewinding_graph1 and self.viewer1.viewRange()[0][1] == self.viewer1.x_axis[-1]:
                self.play_pause_graph1()
        else:
            if not self.is_rewinding_graph2 and (self.viewer2.viewRange()[0][1] == self.viewer2.x_axis[-1]):
                self.play_pause_graph2()
            pass

    def go_to_real_time_page(self):
        page_index = self.Pages.indexOf(self.findChild(QWidget, 'RealTimePage'))
        if page_index != -1:
            self.Pages.setCurrentIndex(page_index)

    def link_graphs(self):
        if self.is_linked:
            self.LinkGraphsButton.setIcon(self.LinkImage)
            if len(self.viewer1.channels) and len(self.viewer2.channels):
                self.viewer1.setXLink(self.viewer2)
                self.viewer1.setYLink(self.viewer2)
        else:
            self.LinkGraphsButton.setIcon(self.UnlinkImage)
            self.viewer1.setXLink(None)
            self.viewer1.setYLink(None)
        self.is_linked = not self.is_linked
    
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