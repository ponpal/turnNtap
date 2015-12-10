from Tkinter import *
from threading import Timer
import tkFont
import collections

class MainApp:
    def __init__(self, master):
        self.master = master
        master.title("Turn N Tap (Exclusive Beta)")
        
        self.categories = ["Beer", "Cocktail", "Spirit", "Wine"]

        self.beers     = ["A", "B", "C", "D", "E"]
        self.cocktails = ["F", "G", "H", "I", "J"]
        self.spirits   = ["K", "L", "M", "N", "O"]
        self.wines     = ["P", "Q", "R", "S", "T"]

        self.categoryMap = [self.beers, self.cocktails, self.spirits, self.wines]

        self.order = {} # Dictionary containing ordered drinks and quantities

        self.tutorialtext = ("1. Turn wheels to select drink.   " +
                             "2. Press right wheel to add drink to order.   3. Pull tap to order.")

        self.lbw = 26 # Listbox width in characters
        self.lbh = 14 # Listbox height in rows

        self.fnt = tkFont.Font(master, size=20, family="Noto Sans")
    
        self.catlabel = Label(master, text="Type of drink")
        self.catlabel["font"] = self.fnt
        self.catlabel.grid(row=0, column=0)
        
        self.catbox = Listbox(master, exportselection=0,
                              selectbackground="orangered",
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
                                selectbackground="lime",
                                width=self.lbw, height=self.lbh, bd=10)
        self.drinkbox["font"] = self.fnt
        self.drinkbox.grid(row=1, column=1)
        self.drinkbox.insert(END, *self.categoryMap[0])
            
        self.orderlabel = Label(master, text="Your order")
        self.orderlabel["font"] = self.fnt
        self.orderlabel.grid(row=0, column=2)

        self.orderbox = Listbox(master, width=self.lbw, height=self.lbh, bd=10, bg="paleturquoise")
        self.orderbox["font"] = self.fnt
        self.orderbox.grid(row=1, column=2)
        self.orderbox["takefocus"] = 0

        self.infolabel = Label(master, text=self.tutorialtext)
        self.infolabel["font"] = self.fnt
        self.infolabel.grid(row=2, columnspan=3)

        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)

        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
        master.grid_rowconfigure(2, weight=4)

        self.catbox.focus_set()
        self.catbox.selection_set(0)
        self.drinkbox.selection_set(0)
        self.drinkbox.activate(0)
        master.bind('<space>', self.addToOrder)
        master.bind('<Delete>', self.removeFromOrder)
        master.bind('<Return>', self.sendOrder)
        
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

        Timer(5, self.resetinfolabel, ()).start()

    # Update drink selection according to category
    def onSelect(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])

        self.drinkbox.delete(0, END)
        self.drinkbox.insert(0, *self.categoryMap[index])
        self.drinkbox.selection_set(0)
        self.drinkbox.activate(0)

if __name__ == "__main__":
    root = Tk()
    main = MainApp(root)
    root.mainloop()
    
