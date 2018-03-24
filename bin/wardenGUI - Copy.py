from platform import system as system_name  
from subprocess import call as system_call 
import paramiko
from tkinter import *#, ttk from tkinter import ttk
import os
import time
import datetime
import threading
from threading import Thread
import socket
import subprocess

#Video related
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk	
from imutils.video import FPS, WebcamVideoStream, FileVideoStream
import imutils		

class App:
	def __init__(self,master,res):		
		#Sets the icon and titlebar text (Quite unnecessary but looks better)
		master.iconbitmap('c:\Python34\DLLs\py.ico')		
		
		#Pass the parameter master to variable self.master
		self.master = master		
		
		#key binding definition for f key to fullscreen function
		self.master.bind('<Key>', self.event_handler)
		
		#Fullscreen status checks the fullscreen status when key or mouse enters/exits fullscreen
		self.fullscreen_status = False		
		
		#set the titlebar text
		self.master.title("WARDEN GUI")			

		##Set the video source
		#self.vs = cv.VideoCapture("rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream")
		#self.vs = WebcamVideoStream(src="rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()
		#self.vs = WebcamVideoStream('C:\\Users\\paultobias\\Downloads\\MOV_1114.mp4')		

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
		self.frame1 = Label(self.master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')
		self.frame1.grid_rowconfigure(0,weight = 1)
		self.frame1.grid_columnconfigure(0,weight = 1)
		
		self.video_frame = Label(self.frame1,width=self.frame1.winfo_width(),height=self.frame1.winfo_height(),background="black")
		self.video_frame.grid(sticky='nsew')
		
		#bind double mouse click to the image_box
		self.video_frame.bind('<Double-Button>', self.event_handler)
		
		#Frame 2 buttons
		self.frame2 = Frame(self.master, background="black")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')	

		
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
		self.console_file_exists = False
		self.console_modified_time = 0
		self.console_file_path = '/home/pi/console.txt'
		#self.console_file_path = 'C://Users//paultobias//Desktop//console.txt'
		#Check remote console file exists		
		
		#Frame 4 image of map
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	
		self.frame4.grid_rowconfigure(0,weight = 1)
		self.frame4.grid_columnconfigure(0,weight = 1)
		
		self.image_frame = Label(self.frame4,width=self.frame4.winfo_width(),height=self.frame4.winfo_height(),background="black")
		self.image_frame.grid(sticky = 'nsew')
		
		self.img_path = 'C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\pic.jpg'		
		
		##initialise
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		
		self.video_conn_ready = False
		self.pi_conn_ready = False
		
		self.video_ready = False		
		self.ssh_ready = False		
		
		self.console_thread = threading.Thread(target=self.write_to_console,args=())
		self.console_thread.daemon = True
		self.console_thread.start()
		
		self.video_feed_thread = Thread(target=self.video_feed,args=())
		self.video_feed_thread.daemon = True
		self.video_feed_thread.start()	
		
		self.video_feed_init_thread = Thread(target=self.video_feed_initialiser,args=())
		self.video_feed_init_thread.daemon = True
		self.video_feed_init_thread.start()
		
		self.conn_thread = threading.Thread(target=self.conn_ready,args=())
		self.conn_thread.daemon = True
		self.conn_thread.start()	
		
		self.img_thread = threading.Thread(target=self.image_update,args=())
		self.img_thread.daemon = True
		self.img_thread.start()		
	
	def conn_ready(self):			
		while True:	
			pi = os.system("ping -n 1 " + '192.168.1.176')
			video = os.system("ping -n 1 " + '192.168.1.10')
			
			if pi == 0:
				self.pi_conn_ready = True
			else:
				self.pi_conn_ready = False	
				self.ssh_ready = False				
			if video == 0:
				self.video_conn_ready = True
			else:
				self.video_conn_ready = False
				self.video_ready = False				
			time.sleep(3)
			
	def video_feed_initialiser(self):
		if not self.video_ready:
			if self.video_conn_ready:			
				self.vs = WebcamVideoStream(src="rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()		
				if str(self.vs.read()) != 'None'	:			
					self.video_ready = True					
		self.master.after(1000, self.video_feed_initialiser)	
	
	def image_update(self):
		self.raw_img = Image.open(self.img_path)		
		self.raw_img = self.raw_img.resize((self.image_frame.winfo_width(),self.image_frame.winfo_height()), Image.ANTIALIAS)
		#self.raw_img = self.raw_img.resize((100,100), Image.ANTIALIAS)
		
		self.img = ImageTk.PhotoImage(self.raw_img)
		#self.img = Image.open('pic.jpg')
		# self.image_frame.winfo_width(),self.image_frame.winfo_height()
		#self.img = ImageTk.Image.open('pic.jpg')	
		
		# self.img = self.raw_img.resize((self.image_frame.winfo_width(),self.image_frame.winfo_height()),Image.ANTIALIAS)
		#self.img = self.raw_img.resize((250, 250), Image.ANTIALIAS)
		self.image_frame.config(image=self.img)
		
		# self.pic_box = Canvas(self.frame4,background="black")
		# # self.pic_box.gridCanvas_rowconfigure(0,weight = 0)
		# # self.pic_box.grid_columnconfigure(0,weight = 0)

		# self.pic_box.grid(sticky='nsew')
		# self.pic_box.config(image=self.img)	
		
		self.master.after(1000, self.image_update)
		
	def video_feed(self):		
		if self.video_ready:					
			frame = self.vs.read()	#read the next frame			
			##resize the image
			if self.video_frame.winfo_width()>1:	
				if self.video_frame.winfo_height() < int((self.video_frame.winfo_width()*0.5625)): 
					frame = imutils.resize(frame 
						,width=int(self.video_frame.winfo_height()*1.77777) #image width
						,height=self.video_frame.winfo_height()#image height
						) 				
				else:
					frame = imutils.resize(frame
						,width=self.video_frame.winfo_width()	#image width
						,height=int((self.video_frame.winfo_width()*0.5625))
						)	#image height					
			##process the raw frame
			cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)	#colours picture correctly		
			current_image = Image.fromarray(cvimage)	#Something to do with PIL, processes the matrix array			
			imagetk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
			self.video_frame.imgtk = imagetk  # stops garbage collection		
			self.video_frame.config(image=imagetk)  # show the image in image_box	
		self.master.after(50, self.video_feed)# cause the function to be called after X milliseconds
		
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
		try:
			self.console_fhandle = self.ftp_client.open(self.console_file_path)
			modifiedtime = self.ftp_client.stat(self.console_file_path).st_mtime		
		except:
			self.console_file_exists = False	
		if self.console_file_exists:							
			if modifiedtime != self.console_modified_time:
				self.console_list = []##need to change this to check line number difference and only bring new lines						
				for line in	self.console_fhandle:					
					self.console_list.append(line)
	
				self.textArea.config(state=NORMAL)
				self.textArea.delete('1.0', END)
				self.textArea.config(state=DISABLED)
				
				for item in self.console_list:
					self.textArea.config(state=NORMAL)					
					self.textArea.insert(END,item)
					self.textArea.config(state=DISABLED)
					self.textArea.see("end")
				self.console_modified_time = modifiedtime
				self.console_fhandle.close()
		else:
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")
			self.textArea.config(state=DISABLED)
			self.ssh_ready = False
			try:
				self.ssh.connect('192.168.1.176', username='pi', password='raspberry')	
				self.ftp_client=self.ssh.open_sftp()		
				self.console_fhandle = self.ftp_client.open(self.console_file_path)
				if self.console_fhandle:
					self.console_file_exists = True
			except:
				pass
		self.master.after(1000, self.write_to_console)	
	
#resolution - height,width	
res = (400,600)

if __name__ == '__main__':
	#create tkinter root
	root = Tk()
	#create instance of app class
	app = App(root,res)	
	root.mainloop()		