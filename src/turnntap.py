from Tkinter import *
from threading import Timer
import tkFont
import collections

categories = ["Beer", "Cocktail", "Spirit", "Wine"]

beers =     ["A", "B", "C", "D", "E"]
cocktails = ["F", "G", "H", "I", "J"]
spirits =   ["K", "L", "M", "N", "O"]
wines =     ["P", "Q", "R", "S", "T"]

categoryMap = [beers, cocktails, spirits, wines]

order = {} # Dictionary containing ordered drinks and quantities

tutorialtext = ("1. Turn wheels to select drink.   " +
"2. Press right wheel to add drink to order.   3. Pull tap to order.")

lbw = 26 # Listbox width in characters
lbh = 14 # Listbox height in rows

master = Tk()
master.title("Turn N Tap (Exclusive Beta)")

fnt = tkFont.Font(master, size=20, family="Noto Sans")

# Update drink selection according to category
def onSelect(evt):
    w = evt.widget
    index = int(w.curselection()[0])

    drinkbox.delete(0, END)
    drinkbox.insert(0, *categoryMap[index])
    drinkbox.selection_set(0)
    drinkbox.activate(0)

catlabel = Label(master, text="Type of drink")
catlabel["font"] = fnt
catlabel.grid(row=0, column=0)
    
catbox = Listbox(master, exportselection=0,
                 selectbackground="orangered",
                 width=lbw, height=lbh, bd=10)
catbox["font"] = fnt
catbox.bind('<<ListboxSelect>>', onSelect)
catbox.grid(row=1, column=0)
for x in categories:
    catbox.insert(END, x)

drinklabel = Label(master, text="Drink")
drinklabel["font"] = fnt
drinklabel.grid(row=0, column=1)
    
drinkbox = Listbox(master, exportselection=0,
                   selectbackground="lime",
                   width=lbw, height=lbh, bd=10)
drinkbox["font"] = fnt
drinkbox.grid(row=1, column=1)
drinkbox.insert(END, *categoryMap[0])

orderlabel = Label(master, text="Your order")
orderlabel["font"] = fnt
orderlabel.grid(row=0, column=2)

orderbox = Listbox(master, width=lbw, height=lbh, bd=10, bg="paleturquoise")
orderbox["font"] = fnt
orderbox.grid(row=1, column=2)
orderbox["takefocus"] = 0

infolabel = Label(master, text=tutorialtext)
infolabel["font"] = fnt
infolabel.grid(row=2, columnspan=3)

master.grid_columnconfigure(0, weight=1)
master.grid_columnconfigure(1, weight=1)
master.grid_columnconfigure(2, weight=1)

master.grid_rowconfigure(0, weight=1)
master.grid_rowconfigure(1, weight=1)
master.grid_rowconfigure(2, weight=4)

# Called whenever a change is made to the order to update UI
def updateOrderListBox():
    orderbox.delete(0, END)

    sortedOrder = collections.OrderedDict(sorted(order.items()))

    for drink, count in sortedOrder.iteritems():
        if count == 1:
            orderbox.insert(END, drink)
        else:
            orderbox.insert(END, drink + " (" + str(count) + ")")

def addToOrder(evt):
    drink = drinkbox.get(drinkbox.curselection()[0])

    if drink in order.keys():
        order[drink] += 1
    else:
        order[drink] = 1

    updateOrderListBox()

def removeFromOrder(evt):
    drink = drinkbox.get(drinkbox.curselection()[0])

    if drink in order.keys():
        if order[drink] > 1:
            order[drink] -= 1
        else:
            del order[drink]

    updateOrderListBox()

def emptyOrder():
    for k in order.keys():
        del order[k]
    updateOrderListBox()

def resetinfolabel():
    infolabel["text"] = tutorialtext
        
def sendOrder(evt):
    if order:
        emptyOrder()
        infolabel["text"] = "Order sent! The bartender will serve you shortly."
    else:
        infolabel["text"] = "Please add some drinks to your order first!"

    Timer(5, resetinfolabel, ()).start()
        
def init():
    catbox.focus_set()
    catbox.selection_set(0)
    drinkbox.selection_set(0)
    drinkbox.activate(0)
    master.bind('<space>', addToOrder)
    master.bind('<Delete>', removeFromOrder)
    master.bind('<Return>', sendOrder)

init()
mainloop()

