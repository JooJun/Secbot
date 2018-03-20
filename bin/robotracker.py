import argparse
import paramiko
from tkinter import *
from tkinter import ttk
import os
import time
import threading

#open cv imports
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk	

class App:
	def __init__(self,master,res):	
	
		# self.ssh = paramiko.SSHClient()
		# self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		# self.ssh.connect('192.168.1.176', username='pi', password='raspberry')
		#Sets the icon and titlebar text (Quite unnecessary but looks better)
		root.iconbitmap('c:\Python34\DLLs\py.ico')		
		
		#Pass the parameter master to variable self.master
		self.master = master
		
		#key binding definition for f key to fullscreen function
		self.master.bind('<Key>', self.event_handler)
		
		self.fullscreen_status = False		
		
		#set the titlebar text
		self.master.title("ROBOTRACKER v1.0")	
		
		self.vs = cv.VideoCapture("rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream")		
		#self.vs = cv.VideoCapture('C:\\Users\\paultobias\\Downloads\\MOV_1114.mp4')
		
		self.raw_image = False
		self.current_image = False
				
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
		
		self.image_box = Label(self.frame1,width=self.frame1.winfo_width(),height=self.frame1.winfo_height(),background="black")
		self.image_box.grid(sticky='nsew')
		
		#bind double mouse click to the image_box
		self.image_box.bind('<Double-Button>', self.event_handler)
		
		#Frame 2 JPEG?
		self.frame2 = Frame(self.master, background="black")
		self.frame2.grid(column = 1, row = 0)	
		self.frame2.grid_rowconfigure(0,weight = 0)
		self.frame2.grid_columnconfigure(0,weight = 0)			
		
		# self.img = ImageTk.PhotoImage(Image.open('C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\pic.jpg'))
		# self.pic_box = Canvas(self.frame2,background="black")
		# # self.pic_box.gridCanvas_rowconfigure(0,weight = 0)
		# # self.pic_box.grid_columnconfigure(0,weight = 0)

		# self.pic_box.grid(sticky='nsew')
		# self.pic_box.config(image=self.img)
		
		
		#frame 3 contains the TEXT BOX
		self.frame3 = Frame(self.master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')	
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		# self.frame3.grid_columnconfigure(1,weight = 1)
				
		self.textArea = Text(self.frame3,wrap=WORD, foreground="black", background="white", width=1, height=1, state=DISABLED)		
		self.textArea.grid(sticky='nsew')
	
		#self.scroll=Scrollbar(self.textArea, orient = VERTICAL)
		# self.scroll=Scrollbar(self.textArea)
		# self.scroll.grid(column=1, row=0, sticky='nsew')
		# self.textArea.config(yscrollcommand=self.scroll.set) 	
		# self.scroll.config(command=self.textArea.yview)			
		
		self.console_fhandle = False		
			
		self.console_modified = 0
		
		#Frame 4 spare for later use
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	
		
		#For video feed
		self.image_box_previous_size = [0,0]
		
	def resize(self,size):
		# if size[0]> 960 or size[1] > 540: 
		# if size[0]> 1280 or size[1] > 720:
			#self.current_image=self.current_image.resize([960,540])
		#else:
		self.current_image=self.current_image.resize(size)
		self.image_box_previous_size = (self.image_box.winfo_width(), self.image_box.winfo_height())
			
	def video_feed(self):
		if self.image_box.winfo_width()>1 and self.image_box_previous_size != (self.image_box.winfo_width(), self.image_box.winfo_height()):			
			if self.image_box.winfo_height() < int((self.image_box.winfo_width()*0.5625)): 
				self.current_size = ([int(self.image_box.winfo_height()*1.77777),(self.image_box.winfo_height())])	

			else:
				self.current_size = ([self.image_box.winfo_width(),int((self.image_box.winfo_width()*0.5625))])
				
		ok, frame = self.vs.read()
		if ok:			
			#key = cv.waitKey(10)			
			cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)			
			self.current_image = Image.fromarray(frame)#PIL stuff ?			
			if self.image_box.winfo_width()>1:				
				self.resize(self.current_size)				
			imagetk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
			self.image_box.imgtk = imagetk  # anchor imgtk so as not be deleted by garbage-collector		
			self.image_box.config(image=imagetk)  # show the image	
		self.master.after(8, self.video_feed)			
	
	def event_handler(self,event=None):			
		if event.char == 'f' or event.keysym == 'Escape' or event.num == 1:
			self.fullscreen(event)	
		if event.char == 'q':
			pass			
			
	def fullscreen(self,event=None):
		if event.char == 'f' or event.num == 1 or event.keysym == 'Escape':
			if self.fullscreen_status == False and (event.char == 'f' or event.num == 1):					
				self.frame1.grid(columnspan = 2,rowspan=2)
				self.frame1.lift()	
				self.fullscreen_status = True			
			else:
				self.frame1.grid(columnspan = 1,rowspan=1)
				self.fullscreen_status = False		
				
	def write_to_console(self):
		ftp_client=self.ssh.open_sftp()
		ftp_client.get('/home/pi/console.txt','C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\console.txt')
		ftp_client.close()
		if self.console_fhandle:
			if self.console_modified != time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime('C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\console.txt'))):
				self.console_list = []
				for line in	self.console_fhandle:
					self.console_list.append(line)				
				for item in self.console_list:
					self.textArea.config(state=NORMAL)
					self.textArea.insert(END,item)
					self.textArea.config(state=DISABLED)
					self.textArea.see("end")
		else:
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")
			self.textArea.config(state=DISABLED)			
			try:			
				self.console_fhandle = open('C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\console.txt','r')
			except:
				pass
		self.master.after(1000, self.write_to_console)
	
#resolution - height,width	
res = (400,600)
#create tkinter root
root = Tk()

#create instance of app class
app = App(root,res)
# #call videofeed and write_to_console functions from app class
app.video_feed()
#app.write_to_console()

try:
#start tkinter mainloop
	root.mainloop()
finally:
	pass