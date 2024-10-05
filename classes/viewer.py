from channel import CustomSignal
class Viewer():
    def __init__(self):
        self.__channels = []
        self.__rewind_state = False
        self.__speed = 1
        pass
    
    def play(self):
        pass
    
    def pause(self):
        pass
    
    def rewind(self):
        pass    
    
    def zoom_in(self):
        pass
    
    def zoom_out(self):
        pass
    
    def add_channel(self , new_channel):
        if isinstance(new_channel , CustomSignal):
            self.__channels.append(new_channel)
        else:
            raise Exception("The new channel must be of class CustomSignal")
    
    def remove_channel(self , to_be_removed_channel):
        self.__channels.remove(to_be_removed_channel)
    
    
    @property
    def speed(self):
        return self.__speed
    
    @speed.setter
    def speed(self , new_speed):
        if(new_speed > 0):
            self.__speed = new_speed
        else: 
            raise Exception("Speed of cine must be greater than zero")
        pass
    
    @property
    def rewind_state(self):
        return self.__rewind_state
    
    @rewind_state.setter
    def rewind_state(self, new_rewind_state):
        self.__rewind_state = new_rewind_state
    
    @property
    def channels(self):
        return self.__channels

