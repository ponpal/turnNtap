from Tkinter import *
from threading import Timer
import tkFont
import collections
import threading
import serial
import Queue

class MainApp:
    def __init__(self, master, queue, endCommand):
        self.master = master
        self.master.title("Turn N Tap (Exclusive Beta)")

        self.queue = queue
        
        self.categories = ["Beer", "Cocktail", "Spirit", "Wine"]

        self.beers     = ["A", "B", "C", "D", "E"]
        self.cocktails = ["F", "G", "H", "I", "J"]
        self.spirits   = ["K", "L", "M", "N", "O"]
        self.wines     = ["P", "Q", "R", "S", "T"]

        self.categoryMap = [self.beers, self.cocktails, self.spirits, self.wines]

        self.order = {} # Dictionary containing ordered drinks and quantities

        self.tutorialtext = ("1. Turn wheels to select drink.   " +
                             "2. Press the green wheel to add drink to order.   " + 
                             "3. Pull tap to order.")

        self.lbw = 26 # Listbox width in characters
        self.lbh = 14 # Listbox height in rows

        self.catPrevious = "None"
        self.drinkPrevious = "None"
        
        self.fnt = tkFont.Font(master, size=20, family="Noto Sans")
    
        self.catlabel = Label(master, text="Type of drink")
        self.catlabel["font"] = self.fnt
        self.catlabel.grid(row=0, column=0)
        
        self.catbox = Listbox(master, exportselection=0,
                              selectbackground="tomato",
                              width=self.lbw, height=self.lbh, bd=10)
        self.catbox["font"] = self.fnt
        self.catbox.bind('<<ListboxSelect>>', self.onSelect)
        self.catbox.grid(row=1, column=0)
        for x in self.categories:
            self.catbox.insert(END, x)
            
        self.drinklabel = Label(master, text="Drink")
        self.drinklabel["font"] = self.fnt
        self.drinklabel.grid(row=0, column=1)
    
        self.drinkbox = Listbox(master, exportselection=0,
                                selectbackground="springgreen",
                                width=self.lbw, height=self.lbh, bd=10)
        self.drinkbox["font"] = self.fnt
        self.drinkbox.grid(row=1, column=1)
        self.drinkbox.insert(END, *self.categoryMap[0])
            
        self.orderlabel = Label(master, text="Your order")
        self.orderlabel["font"] = self.fnt
        self.orderlabel.grid(row=0, column=2)

        self.orderbox = Listbox(master, width=self.lbw,
                                height=self.lbh, bd=10, bg="paleturquoise")
        self.orderbox["font"] = self.fnt
        self.orderbox.grid(row=1, column=2)
        self.orderbox["takefocus"] = 0

        self.infolabel = Label(master, text=self.tutorialtext)
        self.infolabel["font"] = self.fnt
        self.infolabel.grid(row=2, columnspan=3)

        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=4)

        self.catbox.focus_set()
        self.catbox.selection_set(0)
        self.drinkbox.selection_set(0)
        self.drinkbox.activate(0)

        self.activateButtons()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                threadId = msg[0]
                data = msg[1].strip()

                print "Thread: %d" % threadId + "\tMessage: %d" % data
                
                if data in ["R", "G", "B"]:
                    if threadId == 0:
                        if self.catPrevious != "None":
                            self.processRotation(data, self.catPrevious, catbox)

                        self.catPrevious = data
                    else:
                        if self.drinkPrevious != "None":
                            self.processRotation(data, self.drinkPrevious, drinkbox)

                        self.drinkPrevious = data
                            
                else:
                    pass
                    #pressButton(threadId)
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def processRotation(self, color, prev, listbox):
        if ((prev == "G" and color == "R") or
            (prev == "R" and color == "B") or
            (prev == "B" and color == "G")):
            #self.rotateCounterClockwise(threadId, color)
            self.rotate(listbox, -1)
               
        if ((prev == "B" and color == "R") or
            (prev == "R" and color == "G") or
            (prev == "G" and color == "B")):
            #self.rotateClockwise(threadId, color)
            self.rotate(listbox, 1)

    def rotate(self, listbox, rotation):
        listbox.focus_set()
        current = self.catbox.curselection()[0]
        listbox.selection_clear(0, END)
        listbox.selection_set((current + rotation) % listbox.size)
            
    #def rotateCounterClockwise(self, id, color):
    #    if id == 0:
    #        self.catbox.focus_set()
    #        current = self.catbox.curselection()[0]
    #        if current > 0:
    #            self.catbox.selection_clear(0, END)
    #            self.catbox.selection_set(current - 1)

    #        self.catPrevious = color
    #    else:
    #        self.drinkbox.focus_set()
    #        current = self.drinkbox.curselection()[0]
    #        if current < 0:
    #            self.drinkbox.selection_clear(0, END)
    #            self.drinkbox.selection_set(current - 1)

    #        self.drinkPrevious = color
                
    #def rotateClockwise(self, id, color):
    #    if id == 0:
    #        self.catbox.focus_set()
    #        current = self.catbox.curselection()[0]
    #        if current < self.catbox.size() - 1:
    #            self.catbox.selection_clear(0, END)
    #            self.catbox.selection_set(current + 1)

    #        self.catPrevious = color
    #    else:
    #        self.drinkbox.focus_set()
    #        current = self.drinkbox.curselection()[0]
    #        if current < self.drinkbox.size() - 1:
    #            self.drinkbox.selection_clear(0, END)
    #            self.drinkbox.selection_set(current + 1)

    #        self.drinkPrevious = color
            
    # Called whenever a change is made to the order to update UI
    def updateOrderListBox(self):
        self.orderbox.delete(0, END)

        sortedOrder = collections.OrderedDict(sorted(self.order.items()))

        for drink, count in sortedOrder.iteritems():
            if count == 1:
                self.orderbox.insert(END, drink)
            else:
                self.orderbox.insert(END, drink + " (" + str(count) + ")")

    def addToOrder(self, evt):
        drink = self.drinkbox.get(self.drinkbox.curselection()[0])

        if drink in self.order.keys():
            self.order[drink] += 1
        else:
            self.order[drink] = 1

        self.updateOrderListBox()

    def removeFromOrder(self, evt):
        drink = self.drinkbox.get(self.drinkbox.curselection()[0])

        if drink in self.order.keys():
            if self.order[drink] > 1:
                self.order[drink] -= 1
            else:
                del self.order[drink]

        self.updateOrderListBox()

    def emptyOrder(self):
        for k in self.order.keys():
            del self.order[k]
        self.updateOrderListBox()

    def resetinfolabel(self):
        self.infolabel["text"] = self.tutorialtext
        
    def sendOrder(self, evt):
        if self.order:
            self.emptyOrder()
            self.infolabel["text"] = "Order sent! The bartender will serve you shortly."
        else:
            self.infolabel["text"] = "Please add some drinks to your order first!"

        self.deactivateButtons()
            
        Timer(3, self.resetinfolabel, ()).start()
        Timer(3, self.activateButtons, ()).start()

    # Update drink selection according to category
    def onSelect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])

        self.drinkbox.delete(0, END)
        self.drinkbox.insert(0, *self.categoryMap[index])
        self.drinkbox.selection_set(0)
        self.drinkbox.activate(0)

    def activateButtons(self):
        self.master.bind('<space>', self.addToOrder)
        self.master.bind('<Delete>', self.removeFromOrder)
        self.master.bind('<Return>', self.sendOrder)

    def deactivateButtons(self):
        self.master.unbind('<space>')
        self.master.unbind('<Delete>')
        self.master.unbind('<Return>')  

class ThreadedClient():
    def __init__(self, master):
        self.master = master
        
        self.queue = Queue.Queue()
        self.running = 1

        self.gui = MainApp(master, self.queue, self.endApplication) 

        self.thread1 = threading.Thread(target=self.serialreader,
                                        args=(0,"/dev/ttyACM0"))
        self.thread1.start()
        
        #self.thread2 = threading.Thread(target=self.serialreader, args=(1, "/dev/ttyACM1"))
        #self.thread2.start()
                    
        self.periodicCall()

    # Check if queue has any data
    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    # Reads a line from the serial input and puts it on the queue
    def serialreader(self, id, port):
        try:
            ser = serial.Serial(port, 9600)
        except serial.SerialException:
            print ("Couldn't open serial communication port (" +
                   port  + "), please check your connections.")
        else:
            print "Successfully started thread %d" % id + "."
            while self.running:
                msg = ser.readline()
                self.queue.put((id, msg))
                
    def endApplication(self):
        self.running = 0
        
if __name__ == "__main__":
    root = Tk()
    client = ThreadedClient(root)
    root.mainloop()
