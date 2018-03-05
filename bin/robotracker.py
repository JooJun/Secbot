from tkinter import *
from tkinter import ttk

text = "This is a test"

class App():

	def __init__(self,master):	
		
		master.title("ROBOTRACKER v1.0")
		master.grid_rowconfigure(0, weight=1)
		master.grid_rowconfigure(1, weight=1)
		master.grid_columnconfigure(0, weight=1)		
		master.grid_columnconfigure(1, weight=1)
		master.minsize(600,480)		
		
		frame1 = Frame(master, background="grey")
		frame1.grid(column = 0, row = 0, sticky='nsew')	

		frame2 = Frame(master, background="green")
		frame2.grid(column = 1, row = 0, sticky='nsew')		

		frame3 = Frame(master, background="white")
		frame3.grid(column = 0, row = 1, sticky='nsew')	

		text_widget=Text(frame3)
		scroll=Scrollbar(frame3)
				

		frame4 = Frame(master, background="bisque")
		frame4.grid(column = 1, row = 1, sticky='nsew')		
				
	def write_to_console(self,text):
		pass
		
		

root = Tk()
app = App(root)

root.mainloop()