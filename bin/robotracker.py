from tkinter import *
from tkinter import ttk
#open cv imports
import numpy as np
import cv2 as cv
from threading import Thread
from PIL import Image, ImageTk	

class App:
	def __init__(self,master,res):			
	
		#Sets the icon and titlebar text (Quite unnecessary but looks better)
		root.iconbitmap('c:\Python34\DLLs\py.ico')		
		
		#Pass the parameter master to variable self.master
		self.master = master
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
		
		#Set the default and minimum resolution (might have to look at this later, default shouldn't necessarily mean minimum
		self.master.minsize(res[0],res[1])		
		
		#Set 4 frames and put them into the grid (grid contains 4 equal boxes)
		
		#Frame 1 will hold the video stream
		self.frame1 = Frame(master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')
		self.frame1.grid_rowconfigure(0,weight = 1)
		self.frame1.grid_columnconfigure(0,weight = 1)
		
		self.image_box = Label(self.frame1,width=1,height=1, background="black")
		self.image_box.grid(sticky='nsew')
		
		#Frame 2
		self.frame2 = Frame(master, background="black")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')		
		
		#frame 3 also contains the text box
		self.frame3 = Frame(master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')	
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		
		self.scroll=Scrollbar()		
		self.textArea = Text(self.frame3,wrap=WORD, yscrollcommand=self.scroll.set, foreground="black", background="white", width=1, height=1, state=DISABLED)		
		self.textArea.grid(column=0,row=0,sticky='nsew')					

		#Frame 4
		self.frame4 = Frame(master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	

		#Some other junk
		# textArea.config(setgrid=frame3)
		# textArea.place(x=0,y=0)		
		# textArea.place(x=1,y=1)
		# textArea.config(state=DISABLED)
		# textArea = Text(frame3, width=50, height=20, wrap=WORD, yscrollcommand=scroll.set, foreground="black")
	
	def video_feed(self):
		
		#print(self.image_box.winfo_width(),self.image_box.winfo_height())			
		ok, frame = self.vs.read()  # read frame from video stream
		# frame = cv.resize(frame, (1280,720))
		if ok:  # frame captured without any errors
			key = cv.waitKey(5)
			cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
			self.current_image = Image.fromarray(cvimage)  # convert image for PIL
			if self.image_box.winfo_width()>1:
				if self.image_box.winfo_height() < int((self.image_box.winfo_width()*0.5625)): 
					self.current_image= self.current_image.resize([int(self.image_box.winfo_height()*1.77777),(self.image_box.winfo_height())])
				else:
					self.current_image= self.current_image.resize([self.image_box.winfo_width(),int((self.image_box.winfo_width()*0.5625))])
			imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter 						
			self.image_box.imgtk = imgtk  # anchor imgtk so as not be deleted by garbage-collector  
			self.image_box.config(image=imgtk)  # show the image
			#self.root.attributes("-fullscreen",True)
		self.master.after(3, self.video_feed)  # call the same function after 30 milliseconds
				
	def write_to_console(self):
		text = open('test_text.txt', 'r')
		self.textArea.config(state=NORMAL)
		self.textArea.insert(INSERT,text.read())		
		self.textArea.config(state=DISABLED)
		text.close()		
		
res = (600,480)
root = Tk()

app = App(root,res)

app.video_feed()
app.write_to_console()

root.mainloop()