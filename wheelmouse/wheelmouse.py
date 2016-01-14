import uinput, threading, serial, Queue

class Wheel():
    def __init__(self, port, axis, mouse):
        self.port = port
        self.axis = axis
        self.mouse = mouse
        self.queue = Queue.Queue()
        self.running = 1
        self.previous = None
    
        self.thread = threading.Thread(target=self.serialreader,
                                        args=(0, port))
        self.thread.start()
        self.periodicCall()

    def processIncoming(self):
        if self.running:
            while self.queue.qsize():
                try:
                    msg = self.queue.get(0).strip()

                    if msg in ["R", "G", "B"]:
                        if self.previous != None and self.previous != msg:
                            rotation = self.rotate(self.previous, msg)
                            self.moveMouse(rotation)
                            
                        self.previous = msg
                    elif msg == "addButton":
                        self.leftClick()
                    elif msg == "deleteButton":
                        self.rightClick()
                except Queue.Empty:
                    print "Queue empty"
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                    pass
        
    # Check if queue has any data
    def periodicCall(self):
        self.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        threading.Timer(0.005, self.periodicCall, ()).start()
        
    def rotate(self, prev, curr):
        if ((prev == "G" and curr == "R") or
            (prev == "R" and curr == "B") or
            (prev == "B" and curr == "G")):
            return -10
        elif ((prev == "B" and curr == "R") or
              (prev == "R" and curr == "G") or
              (prev == "G" and curr == "B")):
            return 10
        else:
            return 0
            
    def serialreader(self, i, port):
        try:
            ser = serial.Serial(port, 9600)
        except serial.SerialException:
            print ("Couldn't open serial communication port (" +
                   port  + "), please check your connections.\n")
        else:
            print "Successfully started thread (" + port + ").\n"
            while True:
                msg = ser.readline()
                self.queue.put(msg)

    def moveMouse(self, value):
        if self.axis == "x":
            self.mouse.emit(uinput.REL_X, value)
        else:
            self.mouse.emit(uinput.REL_Y, value)

    def leftClick(self):
        print "Left click"
        self.mouse.emit(uinput.BTN_LEFT, 1)
        self.mouse.emit(uinput.BTN_LEFT, 0)

    def rightClick(self):
        print "Right click"
        self.mouse.emit(uinput.BTN_RIGHT, 1)
        self.mouse.emit(uinput.BTN_RIGHT, 0)
        
if __name__ == "__main__":
    events = (uinput.REL_X,
              uinput.REL_Y,
              uinput.BTN_LEFT,
              uinput.BTN_RIGHT,)

    mouse = uinput.Device(events)
    
    wheel1 = Wheel("/dev/ttyACM0", "x", mouse)
    wheel2 = Wheel("/dev/ttyUSB0", "y", mouse)

