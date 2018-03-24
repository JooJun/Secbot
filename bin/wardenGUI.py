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
		self.console_count = 0
		self.console_file_path = '/home/pi/console.txt'
		#self.console_file_path = 'C://Users//paultobias//Desktop//console.txt'			
		
		#Frame 4 image of map
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	
		self.frame4.grid_rowconfigure(0,weight = 1)
		self.frame4.grid_columnconfigure(0,weight = 1)
		
		self.image_frame = Label(self.frame4,width=self.frame4.winfo_width(),height=self.frame4.winfo_height(),background="black")
		self.image_frame.grid(sticky = 'nsew')
		
		self.img_path = 'C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\pic.jpg'	
		self.img_modified_time = 0
		
		#ssh settings
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
		
		self.console_list = []
	
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
			time.sleep(5)
			
	def video_feed_initialiser(self):
		if not self.video_ready:
			if self.video_conn_ready:			
				self.vs = WebcamVideoStream(src="rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()		
				if str(self.vs.read()) != 'None'	:			
					self.video_ready = True					
		self.master.after(1000, self.video_feed_initialiser)	
	
	def image_update(self):
		modified_time = os.path.getmtime(self.img_path)
		if modified_time != self.img_modified_time:
			self.raw_img = Image.open(self.img_path)	
			self.img_modified_time = modified_time		
		if self.raw_img.width != self.image_frame.winfo_width():
			self.raw_img = Image.open(self.img_path)	
			self.raw_img = self.raw_img.resize((self.image_frame.winfo_width(),self.image_frame.winfo_height()), Image.ANTIALIAS)
			self.img = ImageTk.PhotoImage(self.raw_img)		
			self.image_frame.config(image=self.img)		
		self.master.after(50, self.image_update)
		
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
			
		else:
			try:
				self.video_frame.config(image=self.img)
			except:
				pass
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
	
	# def ssh_establish(self):		
		# if self.ssh_ready == False and self.pi_conn_ready == True:			
			# try:				
				# self.ssh.connect('192.168.1.176', username='pi', password='raspberry')	
				# self.ftp_client=self.ssh.open_sftp()
				# self.ssh_ready = True		
			# except:
				# pass

	def write_to_console(self):	
		# print(self.ssh_ready, self.console_file_exists)
		try:	
			modifiedtime = self.ftp_client.stat(self.console_file_path).st_mtime	
			# print (modifiedtime)
		except:
			self.console_file_exists = False
			self.modified_time = 0
			self.console_count = 0
			self.console_list = []			
			# try:
				# self.ssh.exec_command('ls', timeout=5)				
			# except:
				# self.ssh_ready = False				
		if self.console_file_exists:
			# print("file exists")			
			if modifiedtime != self.console_modified_time or len(self.console_list) <1:
				# print("times are different")
				#print(self.console_fhandle.readlines())
				file_temp = self.console_fhandle.readlines()
				# print(file_temp)
				for item in file_temp:
					# print(item)
					self.console_list.append(item)
				list_length = len(self.console_list)
				while self.console_count < list_length-1:
					self.textArea.config(state=NORMAL)		
					self.textArea.insert(END,self.console_list[self.console_count])
					self.textArea.config(state=DISABLED)
					self.textArea.see("end")
					self.console_count+=1
				self.console_modified_time = modifiedtime			
		else:
			# try:			
				# self.ssh.exec_command('ls', timeout=5)
			# except:
				# self.ssh_ready = False
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")			
			self.textArea.config(state=DISABLED)
			
			self.console_count = 0	
			if self.ssh_ready == True:
				if self.console_fhandle:
					self.console_fhandle.close()
				#self.console_fhandle = self.ftp_client.open(self.console_file_path)	
				try:
					self.console_fhandle = self.ftp_client.open(self.console_file_path)	
					self.console_file_exists = True					
					self.textArea.config(state=NORMAL)
					self.textArea.delete('1.0', END)
					self.textArea.config(state=DISABLED)
				except:
					self.console_file_exists = False					
			else:
				# self.ssh_establish()
				if self.ssh_ready == False and self.pi_conn_ready == True:
					# print("got here")
					try:				
						self.ssh.connect('192.168.1.176', username='pi', password='raspberry')	
						self.ftp_client=self.ssh.open_sftp()
						self.ssh_ready = True		
					except:
						pass
		self.master.after(1000, self.write_to_console)		
		
#Opening resolution - height,width	
res = (400,600)

if __name__ == '__main__':
	#create tkinter root
	root = Tk()
	#create instance of app class
	app = App(root,res)	
	root.mainloop()		