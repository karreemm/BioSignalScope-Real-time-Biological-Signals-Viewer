class Navigations:
    def initialize(self, NonRectangleSignalButton, BackHomeButton1, BackHomeButton2, BackHomeButton3, RealTimeSignalButton, RealTimeSignalPage, MainPage, NonRectangleSignalPage, Pages):
        self.NonRectangleSignalButton = NonRectangleSignalButton
        self.BackHomeButton1 = BackHomeButton1
        self.BackHomeButton2 = BackHomeButton2
        self.BackHomeButton3 = BackHomeButton3
        self.RealTimeSignalButton = RealTimeSignalButton
        self.RealTimeSignalPage = RealTimeSignalPage
        self.MainPage = MainPage
        self.NonRectangleSignalPage = NonRectangleSignalPage
        self.Pages = Pages

    def go_to_non_rectangle_signal_page(self):
        if self.NonRectangleSignalPage != -1:
            self.Pages.setCurrentIndex(self.NonRectangleSignalPage)
    
    def go_to_home_page(self):
        if self.MainPage != -1:
            self.Pages.setCurrentIndex(self.MainPage)
