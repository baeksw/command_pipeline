import time 
import functools
from enum import Enum
from abc import ABCMeta, abstractclassmethod

def coroutine(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        generator = function(*args, **kwargs)
        next(generator)
        return generator
    return wrapper


class EventType(Enum):
    EVENT_01 = 1
    EVENT_02 = 2
    EVENT_03 = 3
    NONE = 89
    EXTRA = 99

class Event:
    def __init__(self, kind):
        self.__kind = kind 
    
    @property
    def kind(self):
        return self.__kind
    
    @kind.setter
    def kind(self, value):
        self.__kind = value 

class CmdInvoker:
    
    def __init__(self):
        self._commands = {}
        self._history = []
    
    @property 
    def history(self):
        return self._history
    
    def register(self, command_name, command):
        self._commands[command_name] = command
        
    def execute(self, command_name):
        if command_name in self._commands.keys():
            self._history.append((time.time(), command_name))
            self._commands[command_name].execute()
        else:
            print(f"Command [{command_name}] not recognised")
             
@coroutine
def handler_event00(successor, cmd_invoker ):
    while True:
        event = (yield)
        if event.kind == EventType.EVENT_01: 
            cmd_invoker.execute(event.kind)
        elif successor is not None:
            successor.send(event)

@coroutine
def handler_event01(successor, cmd_invoker ):
    while True:
        event = (yield)
        if event.kind == EventType.EVENT_02: 
            cmd_invoker.execute(event.kind)
        elif successor is not None:
            successor.send(event)
    
def build_pipeline(ff):
    pipeline = handler_event00(None, ff)
    pipeline = handler_event01(pipeline, ff)
    return pipeline


class ICommand(metaclass=ABCMeta):
    ''' '''
    @abstractclassmethod
    def execute(self):
        ''' The required '''
        
class SwitchOnCommand(ICommand):
    def __init__(self, light):
        self._light = light
        
    def execute(self):
        self._light.turn_on()

class SwitchOffCommand(ICommand):
    def __init__(self, light):
        self._light = light
        
    def execute(self):
        self._light.turn_off()
        
class Light():

    def turn_on(self):
        print('turn on light.')

    def turn_off(self):
        print('turn off light.')
        
        
if __name__ == '__main__':
    light = Light()
    ff = CmdInvoker()
    ff.register(EventType.EVENT_01, SwitchOnCommand(light))
    ff.register(EventType.EVENT_02, SwitchOffCommand(light))
    pipeline = build_pipeline(ff)
    pipeline.send(Event(EventType.EVENT_01))
    pipeline.send(Event(EventType.EVENT_02))

