import Tkinter as tk

root = tk.Tk()
deli = 100           # milliseconds of delay per character
svar = tk.StringVar()
labl = tk.Label(root, width=1000,textvariable=svar, height=10 )

def shif():
    shif.msg = shif.msg[1:] + shif.msg[0]
    svar.set(shif.msg)
    root.after(deli, shif)

shif.msg = ' Is this an alert, or what? '
shif()
labl.pack(fill='x')
root.mainloop()