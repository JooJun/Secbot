from __future__ import print_function #For openCV

from tkinter import *
from tkinter import ttk

#For openCV

from PIL import Image
from PIL import ImageTk
import threading
import datetime
import time
import imutils
import cv2
import os

class videoStream:
	def __init__(self,vs,output_path = "./"):
		self.vs = vs
		self.outputPath = output_path
		self.frame = None
		self.thread = None
		self.stopEvent = None
		self.panel = None		  
		
		# start a thread that constantly pools the video sensor for
		# the most recently read frame
		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()
 
		# set a callback to handle when the window is closed
		self.root.wm_title("PyImageSearch PhotoBooth")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
		

class App:
	def __init__(self,master,res):	
	
		videostream = videoStream(cv2.VideoCapture(0))
			
	
		#Sets the icon and titlebar text (Quite unnecessary but looks better
		root.iconbitmap(r'c:\Python34\DLLs\py.ico')		
		
		#Pass the parameter master to variable self.master
		self.master = master
		#set the titlebar text
		self.master.title("ROBOTRACKER v1.0")	
		
		#Configure the master frame's grid
		self.master.grid_rowconfigure(0, weight=1)
		self.master.grid_rowconfigure(1, weight=1)
		self.master.grid_columnconfigure(0, weight=1)		
		self.master.grid_columnconfigure(1, weight=1)
		
		#Set the default and minimum resolution (might have to look at this later, default shouldn't necessarily mean minimum
		self.master.minsize(res[0],res[1])		
		
		#Set 4 frames and put them into the grid (grid contains 4 equal boxes)
		
		#Frame 1 will hold the video stream
		self.frame1 = Frame(master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')	
		
		#Frame 2
		self.frame2 = Frame(master, background="green")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')		
		
		#frame 3 also contains the text box
		self.frame3 = Frame(master, background="white")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')	
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		
		self.scroll=Scrollbar()		
		self.textArea = Text(self.frame3,wrap=WORD, yscrollcommand=self.scroll.set, foreground="green", background="black", width=1, height=1, state=DISABLED)		
		self.textArea.grid(column=0,row=0,sticky='nsew')					

		#Frame 4
		self.frame4 = Frame(master, background="bisque")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	

		#Some other junk
		# textArea.config(setgrid=frame3)
		# textArea.place(x=0,y=0)		
		# textArea.place(x=1,y=1)
		# textArea.config(state=DISABLED)
		# textArea = Text(frame3, width=50, height=20, wrap=WORD, yscrollcommand=scroll.set, foreground="black")
				
	def write_to_console(self):
		text = open('test_text.txt', 'r')
		self.textArea.config(state=NORMAL)
		self.textArea.insert(INSERT,text.read())		
		self.textArea.config(state=DISABLED)
		text.close()
		
res = (600,480)
root = Tk()
app = App(root,res)

print("[INFO] warming up camera...")
vs = VideoStream(0)#.start()
time.sleep(2.0)

vsa = videoStream(vs)

# app.write_to_console()

# try:	
# except:
	# response = input("Error")

root.mainloop()