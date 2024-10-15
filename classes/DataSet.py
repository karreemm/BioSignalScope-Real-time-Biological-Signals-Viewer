# a class that's required to open a CSV file and extract proper information from it and save these atttributes
import pandas as pd

class DataSet():
    '''
    A class should be a representation of the data needed to be visulized
    '''
    def __init__(self, path) -> None:
        self.data = pd.read_csv(path)
        self.axis = len(self.data.columns) - 1
    
    