class Linker():
    def __init__(self , signal1 , signal2):
        self.__signal1 = signal1
        self.__signal2 = signal2
        self.__linked_zoom = 1
        self.__linked_cine_speed = 1
        self.__linked_rewind_state = False
        self.__is_linked_paused = False
    
    def play(self):
        self.__is_linked_paused = not self.__is_linked_paused
        pass
    
    def pause(self):
        self.__is_linked_paused = not self.__is_linked_paused
        pass
    
    def rewind(self):
        self.__linked_rewind_state = not self.__linked_rewind_state
        pass    
    
    def zoom_in(self):
        pass
    
    def zoom_out(self):
        pass
        
    @property
    def linked_zoom(self):
        return self.__linked_zoom
    
    @linked_zoom.setter
    def linked_zoom(self , new_zoom):
        if(new_zoom > 0 ):
            self.__linked_zoom = new_zoom
        else:
            raise Exception("Value of zoom must be greater than zero") 
        
    @property
    def linked_cine_speed(self):
        return self.__linked_cine_speed
    
    @linked_cine_speed.setter
    def linked_cine_speed(self , new_cine_speed):
        if(new_cine_speed > 0):
            self.__linked_cine_speed = new_cine_speed
        else: 
            raise Exception("Speed of cine must be greater than zero")
        pass
    
    @property
    def linked_rewind_state(self):
        return self.__linked_rewind_state
    
    # @linked_rewind_state.setter
    # def linked_rewind_state(self, new_rewind_state):
    #     self.__linked_rewind_state = new_rewind_state
        
    @property
    def is_linked_paused(self):
        return self.__is_linked_paused