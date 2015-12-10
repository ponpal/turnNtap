import threading
import logging
import serial

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class ArduinoThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        #self.ser = serial.Serial(kwargs["port"], 9600)
        return

    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        return
        
        #while 1:
        #    line = self.ser.readline()
        #    print line:

for i in range(5):
    t = ArduinoThread(args=(i,), kwargs={'port':'/dev/ttyACM0'})
    t.start()
