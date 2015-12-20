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
        self.buttonsActive = True
        
        self.categories = [" All drinks", " Beers", " Cocktails",
                           " Spirits", " Wines"]
        self.positions = [0, 0, 0, 0, 0]

        self.beers     = [" A", " B", " C", " D", " E"]
        self.cocktails = [" F", " G", " H", " I", " J"]
        self.spirits   = [" K", " L", " M", " N", " O"]
        self.wines     = [" P", " Q", " R", " S", " T"]
        self.allDrinks = self.beers + self.cocktails + self.spirits + self.wines
        
        self.categoryMap = [self.allDrinks, self.beers, self.cocktails,
                            self.spirits, self.wines]
        self.selectedDrink = self.categoryMap[0][0]
        self.order = {} # Dictionary containing ordered drinks and quantities

        self.tutorialtext = ("1. Turn wheels to select drink.   " +
                             "2. Press the + button to add drink to order.   " + 
                             "3. Pull tap to order.")

        self.lbw = 26 # Listbox width in characters
        self.lbh = 14 # Listbox height in rows

        self.catPrevious = None
        self.drinkPrevious = None
        
        self.fnt = tkFont.Font(master, size=21, family="Noto Sans")
    
        self.catlabel = Label(master, text="Drink category")
        self.catlabel["font"] = self.fnt
        self.catlabel.grid(row=0, column=0)
        
        self.catbox = Listbox(master, exportselection=0,
                              selectbackground="tomato",
                              width=self.lbw, height=self.lbh, bd=10,
                              highlightthickness=0)
        self.catbox["font"] = self.fnt
        self.catbox.bind('<<ListboxSelect>>', self.onSelect)
        self.catbox.grid(row=1, column=0)
        for x in self.categories:
            self.catbox.insert(END, x)
            
        self.drinklabel = Label(master, text="Your order")
        self.drinklabel["font"] = self.fnt
        self.drinklabel.grid(row=0, column=1)
    
        self.drinkbox = Listbox(master, exportselection=0,
                                selectbackground="springgreen",
                                width=self.lbw, height=self.lbh, bd=10,
                                highlightthickness=0)
        self.drinkbox["font"] = self.fnt
        self.drinkbox.bind('<<ListboxSelect>>', self.onSelect)
        self.drinkbox.grid(row=1, column=2)
        self.drinkbox.insert(END, *self.categoryMap[0])
            
        self.orderlabel = Label(master, text="Drink")
        self.orderlabel["font"] = self.fnt
        self.orderlabel.grid(row=0, column=2)

        self.orderbox = Listbox(master, selectbackground="light cyan",
                                width=self.lbw, height=self.lbh, bd=10,
                                bg="paleturquoise")
        self.orderbox["font"] = self.fnt
        self.orderbox.grid(row=1, column=1)
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
                
                if data in ["R", "G", "B"]:
                    if threadId == 1:
                        if self.catPrevious != None:
                            self.processRotation(data, self.catPrevious,
                                                 self.catbox)
                            
                        self.catPrevious = data
                    else:
                        if self.drinkPrevious != None:
                            self.processRotation(data, self.drinkPrevious,
                                                 self.drinkbox)

                        self.drinkPrevious = data
                else:
                    print "Thread: %d" % threadId + "\tMessage: " + data
                    if self.buttonsActive:
                        if data == "addButton":
                            self.addToOrder(None)
                        elif data == "deleteButton":
                            self.removeFromOrder(None)
                        elif data == "tapButton":
                            self.sendOrder(None)
                        else:
                            pass

                        self.deactivateButtons()
                        Timer(0.1, self.activateButtons, ()).start()
                        
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass

    def processRotation(self, color, prev, listbox):
        if ((prev == "G" and color == "R") or
            (prev == "R" and color == "B") or
            (prev == "B" and color == "G")):
            self.rotate(listbox, -1)
               
        if ((prev == "B" and color == "R") or
            (prev == "R" and color == "G") or
            (prev == "G" and color == "B")):
            self.rotate(listbox, 1)

    def rotate(self, listbox, rotation):
        listbox.focus_set()
        current = listbox.curselection()[0]
        listbox.selection_clear(0, END)
        next = (current + rotation) % listbox.size()
        listbox.selection_set(next)
        listbox.activate(next)
        listbox.see(next)
        
        self.onSelect2(listbox, next)
            
    # Called whenever a change is made to the order to update UI
    def updateOrderListBox(self):
        self.orderbox.delete(0, END)

        sortedOrder = collections.OrderedDict(sorted(self.order.items()))

        for drink, count in sortedOrder.iteritems():
            if count == 1:
                self.orderbox.insert(END, drink)
            else:
                self.orderbox.insert(END, drink + " (" + str(count) + ")")

        self.markInOrder(self.selectedDrink)
                
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

    def resetOrderBox(self):
        self.emptyOrder()
        self.orderbox["bg"] = "paleturquoise"
        self.orderbox["selectbackground"] = "light cyan"

    def resetPositions(self):
        for i, v in enumerate(self.positions):
            self.positions[i] = 0

        self.catbox.selection_clear(0, END)
        self.catbox.selection_set(0)
        self.catbox.activate(0)
        self.drinkbox.selection_clear(0, END)
        self.drinkbox.selection_set(0)
        self.drinkbox.activate(0)
        self.select(self.catbox, 0, "")
            
    def sendOrder(self, evt):
        if self.order:
            self.orderbox["bg"] = "light gray"
            self.orderbox["selectbackground"] = "light gray"
            self.infolabel["text"] = ("Order sent! " +
                                      "The bartender will serve you shortly.")
        else:
            self.infolabel["text"] = "Please add some drinks to your order first!"

        self.deactivateButtons()
            
        Timer(3, self.resetinfolabel, ()).start()
        Timer(3, self.activateButtons, ()).start()
        Timer(3, self.resetOrderBox, ()).start()
        Timer(3, self.resetPositions, ()).start()

    # Update drink selection according to category
    def onSelect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)

        self.select(w, index, value)

    def onSelect2(self, listbox, index):
        value = listbox.get(index)

        self.select(listbox, index, value)
        
    def select(self, listbox, index, value):
        if listbox == self.drinkbox:
            self.markInOrder(value)
            self.selectedDrink = value
            self.positions[self.catbox.curselection()[0]] = index
            
        elif listbox == self.catbox:
            self.drinkbox.delete(0, END)
            self.drinkbox.insert(0, *self.categoryMap[index])
            self.drinkbox.selection_set(self.positions[index])
            self.drinkbox.activate(self.positions[index])
            self.drinkbox.see(self.positions[index])

            self.selectedDrink = self.categoryMap[index][self.positions[index]]

            self.updateOrderListBox()
            
    def markInOrder(self, selected):
        sortedOrder = collections.OrderedDict(sorted(self.order.items()))
        if selected in sortedOrder:
            self.orderbox.selection_clear(0, END)
            self.orderbox.selection_set(sortedOrder.keys().index(selected))
        else:
            self.orderbox.selection_clear(0, END)

    def activateButtons(self):
        self.buttonsActive = True
        self.master.bind('<space>', self.addToOrder)
        self.master.bind('<Delete>', self.removeFromOrder)
        self.master.bind('<Return>', self.sendOrder)
        self.master.bind('<w>', lambda e, l = self.catbox, r = -1:
                         self.buttonRotate(e, l, r))
        self.master.bind('<s>', lambda e, l = self.catbox, r = 1:
                         self.buttonRotate(e, l, r))
        self.master.bind('<o>', lambda e, l = self.drinkbox, r = -1:
                         self.buttonRotate(e, l, r))
        self.master.bind('<l>', lambda e, l = self.drinkbox, r = 1:
                         self.buttonRotate(e, l, r))

    def deactivateButtons(self):
        self.buttonsActive = False
        self.master.unbind('<space>')
        self.master.unbind('<Delete>')
        self.master.unbind('<Return>')  

    def buttonRotate(self, event, listbox, direction):
        self.rotate(listbox, direction)
        
class ThreadedClient():
    def __init__(self, master):
        self.master = master
        
        self.queue = Queue.Queue()
        self.running = 1
        
        self.gui = MainApp(master, self.queue, self.serialkiller) 

        self.thread0 = threading.Thread(target=self.serialreader,
                                        args=(0,"/dev/ttyACM0"))
        self.thread0.start()
        
        self.thread1 = threading.Thread(target=self.serialreader,
                                        args=(1, "/dev/ttyUSB0"))
        self.thread1.start()
                    
        self.periodicCall()

    # Check if queue has any data
    def periodicCall(self):
        self.gui.processIncoming()
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(5, self.periodicCall)

    # Reads a line from the serial input and puts it on the queue
    def serialreader(self, id, port):
        try:
            ser = serial.Serial(port, 9600)
        except serial.SerialException:
            print ("Couldn't open serial communication port (" +
                   port  + "), please check your connections.\n")
        else:
            print "Successfully started thread %d" % id + ".\n"
            while self.running:
                msg = ser.readline()
                self.queue.put((id, msg))
                
    def serialkiller(self):
        self.running = False
        
if __name__ == "__main__":
    root = Tk()
    client = ThreadedClient(root)
    root.mainloop()
    
