from tkinter import *
from tkinter import ttk

class App:
	def __init__(self,master,res):	
	
		#Sets the icon and titlebar text (Quite unnecessary but looks better
		root.iconbitmap(r'c:\Python34\DLLs\py.ico')
		self.master.title("ROBOTRACKER v1.0")
		#Pass the parameter master to variable self.master and configure the grid
		self.master = master
		
		self.master.grid_rowconfigure(0, weight=1)
		self.master.grid_rowconfigure(1, weight=1)
		self.master.grid_columnconfigure(0, weight=1)		
		self.master.grid_columnconfigure(1, weight=1)
		self.master.minsize(res[0],res[1])		
		
		self.frame1 = Frame(master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')	

		self.frame2 = Frame(master, background="green")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')		

		self.frame3 = Frame(master, background="white")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')	
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		
		self.scroll=Scrollbar()		
		self.textArea = Text(self.frame3,wrap=WORD, yscrollcommand=self.scroll.set, foreground="green", background="black", width=1, height=1)		
		self.textArea.grid(column=0,row=0,sticky='nsew')		

		# textArea.config(setgrid=frame3)
		# textArea.place(x=0,y=0)		
		# textArea.place(x=1,y=1)
		# textArea.config(state=DISABLED)
		# textArea = Text(frame3, width=50, height=20, wrap=WORD, yscrollcommand=scroll.set, foreground="black")		

		self.frame4 = Frame(master, background="bisque")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')		
				
	def write_to_console(self,text):
		textArea.insert(INSERT,text)
		textArea.config(state=DISABLED)
		
res = (600,480)
root = Tk()
app = App(root,res)

print(app.scroll)

# try:	
# except:
	# response = input("Error")

root.mainloop()