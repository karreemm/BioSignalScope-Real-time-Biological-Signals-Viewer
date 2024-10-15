import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

class wave:
    def __init__(self, dir=['EMG', 'ECG', 'RSP_AB'], interp_order='linear'):
        """
        Args:
            - dir: List of the directories of the data sheets in CSV format.
        """
        if len(dir) <= 1 :  
            self.dir = ['emg', 'ECG', 'RSP_AB']
        else: self.dir = dir
        print("Input directories:", dir)

        # Read CSV files and store them in raw_data list
        self.raw_data = [pd.read_csv(f'test_signals/{directory}.csv') for directory in self.dir]
        self.data_columns = [dataframe.columns for dataframe in self.raw_data]
        print(len(self.raw_data))
        # Get the minimum and maximum time across all dataframes
        self.min_time, self.max_time = self.get_time_range(self.raw_data)
        
        # Calculate sampling rates for each dataframe
        self.sampling_rates = [self.calc_sample_rate(df) for df in self.raw_data]
        
        # Use the minimum sampling rate as the target rate
        self.sampling_rate = min(self.sampling_rates)
        self.time_grid = self.create_time_grid(self.min_time, self.max_time, self.sampling_rate)
        
        # Set the interpolation order
        self.interp_order = interp_order
        
        # Resample and combine data
        self.data_samples = self.concatenate_resampled_data(self.raw_data, self.time_grid)
    
    def set_files(self, files):
        self.dir = files
        
            
    def calc_sample_rate(self, dataframe):
        """Calculate the sampling rate of a dataframe based on the time intervals."""
        if len(dataframe) < 2:
            return 1.0  # Default rate if there are fewer than two samples
        return 1.0 / (dataframe['time'][1] - dataframe['time'][0])
    
    def get_time_range(self, dataframes):
        """
        Find the minimum and maximum time values across all dataframes.
        """
        min_time = min([min(dataframes[index]['time']) for index in range(len(dataframes))])
        max_time = max([max(dataframes[index]['time']) for index in range(len(dataframes))])
        print(f"Time range: {min_time} to {max_time}")
        return min_time, max_time

    def create_time_grid(self, min_time, max_time, target_sampling_rate):
        """
        Create a common time grid based on the target sampling rate.
        """
        dt = 1.0 / target_sampling_rate  # Time interval between samples
        common_time_grid = np.arange(min_time, max_time + dt, dt)  # Time values for resampling
        return common_time_grid
    
    def resample_single_dataframe(self, df, target_sampling_rate, interp_order):
        """
        Resample a single dataframe using interpolation to fit the common time grid.
        """
        time_values = df['time'].values  # Original time values
        data_values = df.drop(columns='time').values  # Exclude the 'time' column

        resampled_data = {}
        common_time_grid = self.time_grid
        
        # Interpolate each column separately
        for col_idx, col_name in enumerate(df.columns[1:]):  # Skip 'time' column
            # Create interpolation function
            interp_func = interp1d(time_values, data_values[:, col_idx], kind=interp_order, fill_value="extrapolate")
            # Apply interpolation to the common time grid
            resampled_values = interp_func(common_time_grid)
            resampled_data[col_name] = resampled_values
        
        return resampled_data

    def concatenate_resampled_data(self, raw_dataframes, common_time_grid):
        """
        Combine the resampled data from multiple dataframes into a final dataframe.
        """
        resampled_dataframes = []
        dataframes_length = []
        for idx, dataframe in enumerate(raw_dataframes):
            resampled_data = self.resample_single_dataframe(dataframe, self.sampling_rate, self.interp_order)
            resampled_dataframes.append(resampled_data)
            current_columns = self.data_columns[idx]
            print(f"Length of resampled data for {current_columns[1]}: {len(resampled_data[current_columns[1]])}")
            dataframes_length.append(len(resampled_data[current_columns[1]]))
        
        # Find the minimum length across all resampled data
        min_length = min(dataframes_length)
        print(f"Minimum length of all resampled data: {min_length}")
        
        # Clip all resampled dataframes to the minimum length
        for idx in range(len(resampled_dataframes)):
            for col in resampled_dataframes[idx].keys():
                resampled_dataframes[idx][col] = resampled_dataframes[idx][col][:min_length]  # Clip to min_length
        
        # Combine all resampled data
        resampled_data = {'time': common_time_grid[:min_length]}
        for resampled_df_data in resampled_dataframes:
            resampled_data.update(resampled_df_data)
        
        # Create the final combined dataframe
        resampled_df = pd.DataFrame(resampled_data)
        positive_data = self.shift_columns_to_positive_range(resampled_df)
        print(positive_data)
        return positive_data
    
    def shift_columns_to_positive_range(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Shifts each column in the DataFrame to be positive by adding an independent offset for each column.
        
        Args:
            data (pd.DataFrame): The input DataFrame where the first column is 'time', and other columns contain data.
            offset_value (float): A small positive offset to avoid zero values (default is 0.1).
            
        Returns:
            pd.DataFrame: The adjusted DataFrame with all values shifted to positive independently for each column.
        """
        # Create a copy of the data to avoid modifying the original DataFrame
        adjusted_data = data.copy()
        
        # Shift each column independently
        for col_name in adjusted_data.columns[1:]:  # Skip the 'time' column
            min_value = adjusted_data[col_name].min()
            
            # If the minimum value is negative, shift the column to make all values positive
            if min_value < 0:
                adjusted_data[col_name] += abs(min_value) 
        
        return adjusted_data
