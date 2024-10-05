class CustomSignal():
    def __init__(self, signal, color = "red", label = "signal", visability=True):
        self.__color = color
        self.__label = label
        self.__signal = signal
        self.__visability = visability
        
    @property
    def color(self):
        return self.__color
    
    @property
    def label(self):
        return self.__label
    
    @property
    def signal(self):
        return self.__signal
    
    @property
    def visability(self):
        return self.__visability
    
    @signal.setter
    def signal(self, value):
        if isinstance(value,list):
            self.__signal = value
        else:
            raise Exception("the signal must be a list")
        
    @color.setter
    def color(self, value): ## this function could be modified accourding to the gui
        if isinstance(value,str):
            self.__color = value
        else :
            raise Exception("the color must be a string")  
        
    @label.setter
    def label(self, value): 
        if isinstance(value,str):
            self.__label = value
        else :
            raise Exception("the label must be a string")  
        
    @visability.setter
    def visability(self, value): 
        if isinstance(value,bool):
            self.__visability = value
        else :
            raise Exception("the visability must be a boolean")  
        
    def __len__(self):
        return len(self.__signal)
        
    def get_mean():
        pass
    
    def get_std():
        pass 
    
    def get_min():
        pass 
    
    def get_max():
        pass
    
    def get_duration():
        pass  
    
        