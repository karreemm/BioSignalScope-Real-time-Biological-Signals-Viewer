import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

class wave:
    def __init__(self, files_directories,interp_order='linear'):
        """
        Args:
            - dir: List of the directories of the data sheets in CSV format.
        """
        self.data_files_directories = files_directories
        print("Input directories:", dir)

        self.raw_data = [pd.read_csv(directory) for directory in self.data_files_directories]
        self.data_columns = [dataframe.columns for dataframe in self.raw_data]
        print(f'Number of files: {len(self.raw_data)}')
        
        self.min_time, self.max_time = self.get_time_range(self.raw_data)
        
        self.sampling_rates = [self.calc_sample_rate(df) for df in self.raw_data]
        
        self.offset_values = []
        
        # Set the interpolation order
        self.interp_order = interp_order
        
        # Resample and combine data
    
    def transform_ecg_to_amplitude_phase(self, file_path):
        # Step 1: Read the ECG data from the CSV file
        data = pd.read_csv(file_path)
        
        # Make sure the file contains the correct columns
        print(f'data shape{data.shape}')
        time_values = data['time'].values
        ecg_values = data['value'].values
        
        # Step 2: Perform the Fourier Transform
        fft_result = np.fft.fft(ecg_values)
        freqs = np.fft.fftfreq(len(ecg_values), d=(time_values[1] - time_values[0]))
        
        # Step 3: Calculate amplitude and phase
        amplitude = np.abs(fft_result)
        phase = np.angle(fft_result)
        
        # Step 4: Combine the results into a DataFrame
        amplitude_phase_df = pd.DataFrame({'Frequency': freqs, 'Amplitude': amplitude, 'Phase': phase})
        
        # Return only the positive frequencies (excluding the mirrored part for negative frequencies)
        amplitude_phase_df = amplitude_phase_df[amplitude_phase_df['Frequency'] >= 0].reset_index(drop=True)
        
        return amplitude_phase_df
        
    
    def set_files(self, files):
     self.data_files_directories = files
        
            
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
        
        for col_idx, col_name in enumerate(df.columns[1:]):  
            # Create interpolation function
            interp_func = interp1d(time_values, data_values[:, col_idx], kind=interp_order, fill_value="extrapolate")
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
            current_column = self.data_columns[idx]
            print(f"Length of resampled data for {current_column[1]} is {len(resampled_data[current_column[1]])}")
            dataframes_length.append(len(resampled_data[current_column[1]]))
        
        # Find the minimum length across all resampled data
        min_length = min(dataframes_length)
        print(f"Minimum length of all resampled data: {min_length}")
        
        for idx in range(len(resampled_dataframes)):
            for col in resampled_dataframes[idx].keys():
                resampled_dataframes[idx][col] = resampled_dataframes[idx][col][:min_length-1]  # Clip to min_length
        
        resampled_data = {'time': common_time_grid[:min_length-1]}
        for resampled_df_data in resampled_dataframes:
            resampled_data.update(resampled_df_data)
        
        # Create the final combined dataframe
        resampled_df = pd.DataFrame(resampled_data)
        positive_data, self.offset_values = self.shift_columns_to_positive_range(resampled_df)
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
        offset_values = []
        # Shift each column independently
        for col_name in adjusted_data.columns[1:]:  # Skip the 'time' column
            min_value = adjusted_data[col_name].min()
            
            if min_value < 0:
                adjusted_data[col_name] += abs(min_value)
                offset_values.append(abs(min_value)) 
        
        return adjusted_data, offset_values
