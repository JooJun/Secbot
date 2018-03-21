import paramiko
from tkinter import *
from tkinter import ttk
import os
import datetime
import threading

#Video related
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk	
from imutils.video import FPS
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
import imutils

class App:
	def __init__(self,master,res):			
		#Sets the icon and titlebar text (Quite unnecessary but looks better)
		root.iconbitmap('c:\Python34\DLLs\py.ico')		
		
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
		self.vs = WebcamVideoStream(src="rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()
		
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
		
		#Frame 2 JPEG?
		self.frame2 = Frame(self.master, background="black")
		self.frame2.grid(column = 1, row = 0, sticky='nsew')	
		self.frame2.grid_rowconfigure(0,weight = 0)
		self.frame2.grid_columnconfigure(0,weight = 0)			
		
		self.image_frame = Label(self.frame2,width=self.frame2.winfo_width(),height=self.frame2.winfo_height(),background="black")
		self.image_frame.grid(sticky = 'nsew')
		
		# self.img = ImageTk.PhotoImage(Image.open('C:\\Users\\paultobias\\Documents\\GitHub\\Secbot\\bin\\pic.jpg'))
		#self.img = ImageTk.PhotoImage(Image.open('pic.jpg'))
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
		self.console_modified_time = 0
		self.console_file_path = '/home/pi/console.txt'
		#Check remote console file exists
		self.console_file_exists = False
		
		#Frame 4 spare for later use
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')	
		
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			
		
	def image_update(self):
		imagetk = ImageTk.PhotoImage(Image.open('pic.jpg'))
		self.image_frame.config(image=imagetk)
		self.master.after(2000, self.image_update)
		
	def video_feed(self):		
		frame = self.vs.read()	#read the next frame 
		
		##resize the image if self.video_frame has changed size
		if self.video_frame.winfo_width()>1:	
			if self.video_frame.winfo_height() < int((self.video_frame.winfo_width()*0.5625)): 
				frame = imutils.resize(frame 
					,width=int(self.video_frame.winfo_height()*1.77777) #image width
					,height=self.video_frame.winfo_height()#image height
					) 				
				self.video_frame_previous_size = [
					int(self.video_frame.winfo_height()*1.77777)#set new value for 'previous' width
					,self.video_frame.winfo_height()#set new value for 'previous' height
					]
			else:
				frame = imutils.resize(frame
					,width=self.video_frame.winfo_width()	#image width
					,height=int((self.video_frame.winfo_width()*0.5625)))	#image height
				self.video_frame_previous_size = [
					self.video_frame.winfo_width()#set new value for 'previous' width	
					,int((self.video_frame.winfo_width()*0.5625))#set new value for 'previous' height
					]			
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
		#Check if the file exists
		try:
			self.console_file_exists = self.ftp_client.stat(self.console_file_path)
		except:
			self.console_file_exists = False			
			
		#check if the file and file handle exists
		if self.console_file_exists:						
			modifiedtime = self.ftp_client.stat(self.console_file_path).st_mtime				
			if modifiedtime != self.console_modified_time:	
				file = self.ftp_client.open(self.console_file_path)
				console_list = []								
				for line in	file:					
					console_list.append(line)
				print("got here")	
				self.textArea.config(state=NORMAL)
				self.textArea.delete('1.0', END)
				self.textArea.config(state=DISABLED)
				
				for item in console_list:
					self.textArea.config(state=NORMAL)					
					self.textArea.insert(END,item)
					self.textArea.config(state=DISABLED)
					self.textArea.see("end")
				self.console_modified_time = modifiedtime
				file.close()
		else:
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")
			self.textArea.config(state=DISABLED)
			self.console_file_exists = False
			try:					
				self.ftp_client=self.ssh.open_sftp()
				self.console_fhandle = self.ftp_client.open(self.console_file_path)
				self.ssh.connect('192.168.1.176', username='pi', password='raspberry')
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
	
	# #call the looping functions from the instance
	app.video_feed()
	#app.image_update()
	app.write_to_console()
	
	#start tkinter mainloop
	root.mainloop()	
app.vs.stop()