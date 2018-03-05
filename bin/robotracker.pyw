from tkinter import *
from tkinter import ttk

class App():

	def __init__(self,master):
	
		master.grid_rowconfigure(0, weight=1)
		master.grid_rowconfigure(1, weight=1)
		master.grid_columnconfigure(0, weight=1)		
		master.grid_columnconfigure(1, weight=1)

		#Need to set the default size here
		
		frame1 = Frame(master, background="blue")
		frame1.grid(column = 0, row = 0, sticky='nsew')	

		frame2 = Frame(master, background="green")
		frame2.grid(column = 1, row = 0, sticky='nsew')

		frame2 = Frame(master, background="red")
		frame2.grid(column = 0, row = 1, sticky='nsew')

		frame2 = Frame(master, background="bisque")
		frame2.grid(column = 1, row = 1, sticky='nsew')		
				
	

root = Tk()
app = App(root)

root.mainloop()