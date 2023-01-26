"""
  Threaded OSC server
  Inputs can be defined by setting  a dict in format
  {
    {{"path": "/x", "inputName":"x", "parser": parser, "callback": callback},
    ...
    }

  Available parsers:
  Int
  Ints2
  Ints3

  Callbacks not implemented yet

"""
from threading import Thread, Event
from queue import Queue
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
import sys

class OSCReciever(Thread):
  def __init__( self,
                ip="127.0.0.1",
                port=1249,
                inputs = None):
    Thread.__init__(self)
    self.inputOsc = inputs
    self.dispatcher = Dispatcher()
    self.ip = ip
    self.port = port
    self.inQueue = Queue()
    self.stop_event = Event()

    if(inputs == None):
      self.inputs = [
                {"path": "/x", "parser": "Int1"},
                {"path": "/y", "parser": "Int1"},
                {"path": "/z", "parser": "Int1"},
                {"path": "/xy", "parser": "Ints2"},
                {"path": "/yx", "parser": "Ints2"},
                {"path": "/xyz", "parser": "Ints3"},
                {"path": "/xzy", "parser": "Ints3"},
                {"path": "/yxz", "parser": "Ints3"},
                {"path": "/yzx", "parser": "Ints3"},
                {"path": "/zyx", "parser": "Ints3"},
                {"path": "/zxy", "parser": "Ints3"}
                ]
    else:
      self.inputs = inputs
    self.initDispatchers()
    self.server = osc_server.ThreadingOSCUDPServer(
        (self.ip, self.port), self.dispatcher)
  def run(self):
    # try:
      self.server.serve_forever()
    # except KeyboardInterrupt:
      while not self.stop_event.isSet():
        pass

  def Int1(self, id, unused, value1, *args):
    self.inQueue.put_nowait((id, value1))
  def Ints3(self, id, unused, value1, value2, value3, *args):
    self.inQueue.put_nowait((id, value1, value2, value3))
  def Ints2(self, id, unused, value1, value2, *args):
    self.inQueue.put_nowait((id, value1,value2))
  def stop(self):
    self.stop_event.set()
    self.server.shutdown()
  def get(self):
    values = None
    if not self.inQueue.empty():
      values = self.inQueue.get()
    return values
  def getLast(self):
    values = None
    while not self.inQueue.empty():
      values = self.inQueue.get_nowait()
    return values
  def getWait(self):
    values = None
    if not self.inQueue.empty():
      values = self.inQueue.get()
    return values
  def getAll(self):
    values = []
    while not self.inQueue.empty():
      values.append(self.inQueue.get())
    return values
  def initDispatchers(self):
    for i in self.inputs:
        self.dispatcher.map(i["path"],getattr(self, i["parser"]), "")


if __name__ == "__main__":

  osc = OSCReciever()
  try:
    osc.start()
    while 1:
      values = osc.getLast()
      if values:
        print(values)

  except KeyboardInterrupt:
      print('Interrupted')
      osc.stop()
      sys.exit(0)
  print('Shutdown')
