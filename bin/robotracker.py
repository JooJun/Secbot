import tkinter as tk
from tkinter import ttk

class Interface(tk.Tk):

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		
		# frame_master = tk.Frame(self)

		frame1 = tk.Frame(self, background="bisque")
		# frame1.pack(fill="both", expand=True)
		frame1.grid(column = 0, row = 0)
		frame1.columnconfigure()
		
		frame2 = tk.Frame(self, background="blue")
		# frame2.pack(fill="both", expand=True)
		frame2.grid(column = 1, row = 0,ipadx = 20, ipady = 20)
		
		frame3 = tk.Frame(self, background="red")
		frame3.grid(column = 0, row = 1,ipadx = 20, ipady = 20)
		
		frame4 = tk.Frame(self, background="green")
		frame4.grid(column = 1, row = 1,ipadx = 20, ipady = 20)
		
		# frame1.grid_columnconfigure(0, weight=0)		
		# frame1.grid_rowconfigure(0, weight=0)		

		# frame2 = tk.Frame(self, background = "green")
		# frame2.pack(fill="both", expand=True)
		
		# frame2.grid_columnconfigure(1, weight=0)		
		# frame2.grid_rowconfigure(0, weight=0)	
		
		# frame3 = tk.Frame(self, background="blue")
		# frame3.pack(fill="both", expand=True)
		
		# frame3.grid_columnconfigure(0, weight=0)		
		# frame3.grid_rowconfigure(1, weight=0)		

		# frame4 = tk.Frame(self, background = "red")
		# frame4.pack(fill="both", expand=True)
		
		# frame4.grid_columnconfigure(1, weight=0)		
		# frame4.grid_rowconfigure(1, weight=0)		
	

interface = Interface()
interface.minsize(800, 480)
interface.mainloop()