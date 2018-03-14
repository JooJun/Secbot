from tkinter import *
from tkinter import ttk
#open cv imports
import numpy as np
import cv2 as cv
#from threading import Thread
from PIL import Image, ImageTk	

class App:
	def __init__(self,master,res):	
		#Sets the icon and titlebar text (Quite unnecessary but looks better)
		root.iconbitmap('c:\Python34\DLLs\py.ico')		
		
		#Pass the parameter master to variable self.master
		self.master = master
		#key binding definition for f key to fullscreen function
		self.master.bind('<Key>', self.event_handler)
		
		self.fullscreen_status = False		
		
		#set the titlebar text
		self.master.title("ROBOTRACKER v1.0")
		
		# self.destructor function gets fired when the window is closed (not working)
		# self.master.protocol('ROBOTRACKER v1.0', self.destructor)
				
		self.vs = cv.VideoCapture('C:\\Users\\paultobias\\Downloads\\MOV_1114.mp4')
		#self.vs = cv.VideoCapture("rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream")
		
		#Configure the master frame's grid
		self.master.grid_rowconfigure(0, weight=1)
		self.master.grid_rowconfigure(1, weight=1)
		self.master.grid_columnconfigure(0, weight=1)		
		self.master.grid_columnconfigure(1, weight=1)
		
		#Set the opening resolution, and minsize if required
		#self.master.minsize(res[1],res[0])				
		self.master.geometry(str(res[1])+"x"+str(res[0]))
		
		#Set 4 frames and put them into the grid (grid contains 4 equal boxes)
		
		#Frame 1 will hold the VIDEO STREAM
		self.frame1 = Frame(self.master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')
		self.frame1.grid_rowconfigure(0,weight = 1)
		self.frame1.grid_columnconfigure(0,weight = 1)
		
		self.image_box = Label(self.frame1,width=self.frame1.winfo_width()*5,height=self.frame1.winfo_height()*5,background="black")
		self.image_box.grid(sticky='nsew')		
		#-------------------------------------------------------
		
		#Frame 2 spare for later use
		self.frame2 = Frame(self.master, background="black")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')		
		#-------------------------------------------------------
		
		#frame 3 also contains the TEXT BOX
		self.frame3 = Frame(self.master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')	
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		
		self.scroll=Scrollbar()		
		self.textArea = Text(self.frame3,wrap=WORD, yscrollcommand=self.scroll.set, foreground="black", background="white", width=1, height=1, state=DISABLED)		
		self.textArea.grid(column=0,row=0,sticky='nsew')					
		#-------------------------------------------------------
		
		#Frame 4 spare for later use
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')
		#-------------------------------------------------------
		
	def video_feed(self):				
		ok, frame = self.vs.read()  # read frame from video stream
		if ok:  # frame captured without any errors
			key = cv.waitKey(5)
			cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
			self.current_image = Image.fromarray(cvimage)  # convert image for PIL			
			if self.image_box.winfo_width()>1:
				if self.image_box.winfo_height() < int((self.image_box.winfo_width()*0.5625)): 
					self.current_image=self.current_image.resize([int(self.image_box.winfo_height()*1.77777),(self.image_box.winfo_height())])					
				else:
					self.current_image=self.current_image.resize([self.image_box.winfo_width(),int((self.image_box.winfo_width()*0.5625))])					
			imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter 						
			self.image_box.imgtk = imgtk  # anchor imgtk so as not be deleted by garbage-collector		
			self.image_box.config(image=imgtk)  # show the image			
		self.master.after(10, self.video_feed)  # call the same function after 30 milliseconds
		
	def event_handler(self,event=None):			
		if event.char == 'f' or event.keysym == 'Escape':
			self.fullscreen(event)		
			
	def fullscreen(self,event=None):
		if event.char == 'f':
			if self.fullscreen_status == False:				
				self.frame1.grid(columnspan = 2,rowspan=2)
				self.frame1.lift()
				self.current_image= self.current_image.resize([self.master.winfo_width(),int((self.master.winfo_width()*0.5625))])
				self.fullscreen_status = True			
			else:
				self.frame1.grid(columnspan = 1,rowspan=1)
				self.fullscreen_status = False
		if event.keysym == 'Escape':
			if self.fullscreen_status == True:
				self.frame1.grid(columnspan = 1,rowspan=1)
				self.fullscreen_status = False		
				
	def write_to_console(self):
		text = open('test_text.txt', 'r')
		self.textArea.config(state=NORMAL)
		self.textArea.insert(INSERT,text.read())		
		self.textArea.config(state=DISABLED)
		text.close()	
	
#resolution - height,width	
res = (500,900)
#create tkinter root
root = Tk()

#create instance of app class
app = App(root,res)
#call videofeed and write_to_console functions from app class
app.video_feed()
app.write_to_console()

try:
#start tkinter mainloop
	root.mainloop()
finally:
	pass