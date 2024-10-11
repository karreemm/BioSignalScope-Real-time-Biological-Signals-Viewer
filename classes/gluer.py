from scipy.interpolate import interp1d
import numpy as np
class Gluer():
    def __init__(self, signal_1, signal_2, signal_1_x_values,signal_2_x_values,interpolation_order=1):
        self.__signal_1 = signal_1
        self.__signal_2 = signal_2
        self.__signal_1_x_values = signal_1_x_values
        self.__signal_2_x_values = signal_2_x_values
        # self.__window_start_1 = window_start_1
        # self.__window_start_2 = window_start_2
        # self.__gap_overlap = gap_overlap
        self.__interpolation_order = interpolation_order
    
    @property
    def signal_1(self):
        return self.__signal_1
    
    @property
    def signal_2(self):
        return self.__signal_2
    
    @property
    def signal_1_x_values(self):
        return self.__signal_1_x_values
    
    @property
    def signal_2_x_values(self):
        return self.__signal_2_x_values
    
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
    
    def interpolate(self , interpolation_order):
        if(interpolation_order == 0):
            interpolation_order = "linear"
        if(interpolation_order == 1):
            interpolation_order = "quadratic"
        if(interpolation_order == 2):
            interpolation_order = "cubic"
        if (self.signal_1_x_values[-1] > self.signal_2_x_values[0] ):
            overlap_start = max(min(self.signal_2_x_values) ,min(self.signal_1_x_values))
            overlap_end = min(max(self.signal_2_x_values) ,max(self.signal_1_x_values))
            
            interpolation_function_signal_1 = interp1d(self.signal_1_x_values , self.signal_1.signal ,kind=interpolation_order)
            interpolation_function_signal_2 = interp1d(self.signal_2_x_values , self.signal_2.signal ,kind=interpolation_order)

            x_overlapped = np.linspace(overlap_start , overlap_end , num = 1000)
            
            signal_1_interpolated = interpolation_function_signal_1(x_overlapped)
            signal_2_interpolated = interpolation_function_signal_2(x_overlapped)
            
            y_interpolated = (signal_1_interpolated + signal_2_interpolated) / 2
        else:
            x_gap = np.linspace(self.signal_1_x_values[-1] , self.signal_2_x_values[0], num = 1000)
            data_x = np.concatenate([self.signal_1_x_values, self.signal_2_x_values])
            data_y = np.concatenate([self.signal_1.signal, self.signal_2.signal])
            interpolation_function_data_1 = interp1d(data_x , data_y ,kind=interpolation_order ,fill_value="extrapolate")
            
            # data_1_interpolated = interpolation_function_data_1(x_gap)
            # y_interpolated = data_1_interpolated
            
            # interpolation_function_data_1 = interp1d(data_x_signal_1 , data1_y ,kind='quadratic' ,fill_value='extrapolate')
            # interpolation_function_data_2 = interp1d(self.signal_2_x_values , data2_y ,kind='quadratic', fill_value='extrapolate')
            # data_1_interpolated = interpolation_function_data_1(x_gap)
            # data_2_interpolated = interpolation_function_data_2(x_gap)
            # y_interpolated = (data_1_interpolated + data_2_interpolated) / 2
            
            
            
            # plt.plot(x_gap, y_interpolated , linestyle ='--')
            
            # cs = CubicSpline(data_x, data_y)
            # gap_y = cs(x_gap)
            y_interpolated = interpolation_function_data_1(x_gap)
        return y_interpolated