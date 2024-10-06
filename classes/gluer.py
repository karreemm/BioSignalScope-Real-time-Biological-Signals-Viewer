class Gluer():
    def __init__(self, signal_1, signal_2, window_start_1, window_start_2, gap_overlap, interpolation_order=1):
        self.__signal_1 = signal_1
        self.__signal_2 = signal_2
        self.__window_start_1 = window_start_1
        self.__window_start_2 = window_start_2
        self.__gap_overlap = gap_overlap
        self.__interpolation_order = interpolation_order
    
    @property
    def signal_1(self):
        return self.__signal_1
    
    @property
    def signal_2(self):
        return self.__signal_2
    
    @property
    def window_start_1(self):
        return self.__window_start_1
    
    @property
    def window_start_2(self):
        return self.__window_start_2
    
    @property
    def gap_overlap(self):
        return self.__gap_overlap
    
    @property
    def interpolation_order(self):
        return self.__interpolation_order
    
    # @interpolation_order.setter
    # def interpolation_order(self, value)