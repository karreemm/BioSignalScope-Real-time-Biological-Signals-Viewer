from channel import CustomSignal
class Viewer():
    def __init__(self):
        self.__channels = []
        self.__rewind_state = False
        self.__cine_speed = 1
        self.__zoom = 1
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
    def cine_speed(self):
        return self.__cine_speed
    
    @cine_speed.setter
    def cine_speed(self , new_speed):
        if(new_speed > 0):
            self.__cine_speed = new_speed
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
    
    @property
    def zoom(self):
        return self.__zoom
    
    @zoom.setter
    def zoom(self , new_zoom):
        if(new_zoom > 0 ):
            self.__zoom = new_zoom
        else:
            raise Exception("Value of zoom must be greater than zero")
