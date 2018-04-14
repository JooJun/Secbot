import socket
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
from classes.connect import Connect


#Create config dictionary from file
config = {}
data_send = {}
data_receive = {}

with open("config.txt") as config_file:
	for line in config_file:		
		if not line.strip() == '' and not line.startswith('#'):				
			parts = line.split('=')
			config[parts[0].strip()] = parts[1].strip()

#Video related imports
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk  
from imutils.video import FPS, WebcamVideoStream, FileVideoStream
import imutils          

class App:
	def __init__(self,master,res): 

		# self.config = config
		# self.pi_ip = config['pi_ip']
		# self.cam_ip = config['cam_ip']
		self.pi_username = config['pi_username']
		self.pi_password = config['pi_password']
		
		#Pass the parameter master to variable self.master
		self.master = master

		#Sets the icon and titlebar text (Quite unnecessary but looks better)           
		self.master.iconbitmap('{0}/warden.ico'.format(config['content_folder']))                    
		
		#key binding definition for f key to fullscreen function
		self.master.bind('<Key>', self.event_handler)
		
		#Fullscreen status checks the fullscreen status when key or mouse enters/exits fullscreen
		self.fullscreen_status = False          
		
		#set the titlebar text
		self.master.title("Warden Control Panel")       

		#Configure the master frame's grid
		self.master.grid_rowconfigure(0, weight=1)
		self.master.grid_rowconfigure(1, weight=1)
		self.master.grid_columnconfigure(0, weight=1)           
		self.master.grid_columnconfigure(1, weight=1)
		
		#Set the opening resolution, and minsize if required
		#self.master.minsize(res[1],res[0])                             
		self.master.geometry(str(res[1])+"x"+str(res[0]))
		
	#####Set 4 frames and put them into the grid (grid contains 4 equal boxes)#####
		
	###Frame 1 will hold the VIDEO STREAM###
		self.frame1 = Label(self.master, background="grey")
		self.frame1.grid(column = 0, row = 0, sticky='nsew')
		self.frame1.grid_rowconfigure(0,weight = 1)
		self.frame1.grid_columnconfigure(0,weight = 1)
		
		self.video_frame = Label(self.frame1,width=self.frame1.winfo_width(),height=self.frame1.winfo_height(),background="black")
		self.video_frame.grid(sticky='nsew')
		
		#bind double mouse click to the video frame
		self.video_frame.bind('<Double-Button>', self.event_handler)
		
		#Picture to display when no video present
		self.vid_dis_img_path = '{0}/vid_disconnect.jpg'.format(config['content_folder'])				
		
	###Frame 2 SWITCH / CONTROL PANEL SECTION###		
		
		self.frame2 = Frame(self.master, background='grey')
		self.frame2.grid(column = 1, row = 0,sticky='nsew') 
		self.frame2.grid_rowconfigure(0,weight = 1)
		self.frame2.grid_columnconfigure(0,weight = 1)		
			
		self.switch = Button(self.frame2,width=40,height=100,command=self.switch_handler)		
		self.button_img_raw = Image.open('{0}/button.png'.format(config['content_folder']))
		self.button_img_raw = self.button_img_raw.resize((40,100),Image.ANTIALIAS)		
		self.button_photo = ImageTk.PhotoImage(self.button_img_raw)			
		self.switch.configure(image=self.button_photo)		
		#self.switch.configure(command=self.button_handler('button'))

		#self.switch.grid(sticky='w')		
	
		self.switchpanel_background_img_raw = Image.open('{0}/metallic_background.jpg'.format(config['content_folder']))
		# self.button_img_raw = self.button_img_raw.resize((40,100),Image.ANTIALIAS)		
		self.switchpanel_background_img = ImageTk.PhotoImage(self.switchpanel_background_img_raw)		
		self.frame2_background_label = Label(self.frame2, image=self.switchpanel_background_img)
		self.frame2_background_label.place(x=0, y=0, relwidth=1, relheight=1)		
		
		data_send['control_status'] = 'Manual'					
		
	###frame 3 contains the CONSOLE### (Would like to add scrollbar but doesn't work so far)
		self.frame3 = Frame(self.master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')    
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		# self.frame3.grid_columnconfigure(1,weight = 1)
						
		self.textArea = Text(self.frame3,wrap=WORD, foreground="black", background="white", width=1, height=1, state=DISABLED)          
		self.textArea.grid(sticky='nsew')		
   
		self.console_file_exists = False
		self.console_modified_time = 0
		self.console_remote = config['console_remote']	
		self.console_local = config['content_folder']+"/"+config['console_local']
		self.previous_console_length = 0

	###Frame 4 DEPTHMAP###
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')    
		self.frame4.grid_rowconfigure(0,weight = 1)
		self.frame4.grid_columnconfigure(0,weight = 1)
		
		self.depthmap_frame = Label(self.frame4,width=self.frame4.winfo_width(),height=self.frame4.winfo_height(),background="black")
		self.depthmap_frame.grid(sticky = 'nsew')		
		
		self.depthmap_modified_time = 0
		self.depthmap_file_exists = False
		self.depthmap_img_remote = config['depthmap_file_path_remote'] 
		self.depthmap_img_local = './'+config['content_folder']+config['depthmap_file_path_local'] 
		try:
			os.remove(self.depthmap_img_local)
			os.remove(self.console_local)
		except:
			pass
	##create instance of other classes
		self.connect = Connect(config)		
		
	#Start threads:-
		
		#Console thread
		self.console_thread = threading.Thread(target=self.write_to_console,args=())
		self.console_thread.daemon = True
		self.console_thread.start()
		#self.write_to_console()
		
		#Video feed thread
		self.video_feed_thread = Thread(target=self.video_feed,args=())
		self.video_feed_thread.daemon = True
		self.video_feed_thread.start()          
		
		#Video feed initialiser thread
		self.video_feed_init_thread = Thread(target=self.video_feed_initialiser,args=())
		self.video_feed_init_thread.daemon = True
		self.video_feed_init_thread.start()	
		
		#Update the depthmap thread
		self.depmap_thread = threading.Thread(target=self.depmap_update,args=())
		self.depmap_thread.daemon = True
		self.depmap_thread.start()                 
		
		self.console_list = []
		self.modifiedtime = 0
		
		self.authProblem = False		
		
	def depmap_update(self):
		file_data = self.connect.get_file(self.depthmap_img_remote,self.depthmap_img_local,self.depthmap_modified_time)	
		if file_data:				
			if file_data['file_exists']:					
				if file_data['modified_time'] != self.depthmap_modified_time and file_data['file_size'] != 0:
					self.depthmap_modified_time = file_data['modified_time']	
				self.depthmap_file_exists = True		
		try:
			raw_img = Image.open(self.depthmap_img_local)
			if raw_img.width != self.depthmap_frame.winfo_width():
				raw_img = Image.open(self.depthmap_img_local)        
				raw_img = raw_img.resize((self.depthmap_frame.winfo_width(),self.depthmap_frame.winfo_height()), Image.ANTIALIAS)
				self.img = ImageTk.PhotoImage(raw_img)             
				self.depthmap_frame.config(image=self.img) 
		except:
			self.depthmap_file_exists = False				
		self.master.after(1000, self.depmap_update)
	
	def write_to_console(self):			
		file_data = self.connect.get_file(self.console_remote,self.console_local,self.console_modified_time)
		if file_data and file_data['file_exists']:
			file = open(self.console_local).readlines()
			self.console_modified_time = file_data['modified_time']	
			file_length = len(file)
			if file_length != self.previous_console_length:
				self.previous_console_length = file_length
				#Restrict to only printing tailing 100 lines				
				if file_length > 100:
					file = file[file_length-101:file_length-1]
				#Print lines to the text area
				try:					
					self.textArea.config(state=NORMAL)
					self.textArea.delete('1.0', END)
					for item in file:					
						self.textArea.insert(END,item)	
					self.textArea.config(state=DISABLED)
					self.textArea.see("end")				
				except Exception as msg:
					print ("Exception is on 202"+str(msg))	
			else:
				print("skipped it")
		else:
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")                 
			self.textArea.config(state=DISABLED)
			self.modifiedtime = 0
			self.console_file_exists = False
		self.master.after(1000, self.write_to_console)
	
	def video_feed_initialiser(self):
		if not self.connect.video_ready:
			#print("video feed initilaiser has recognised that self.video_ready is false")
			if self.connect.video_conn_ready:
				#print("attempting to reconnect the video connection")
				self.vs = WebcamVideoStream(src="rtsp://"+self.cam_ip+":554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()              
				if str(self.vs.read()) != 'None':       
					#print("setting video_ready to true (self.vs is not none)")
					self.connect.video_ready = True  
		self.master.after(1000, self.video_feed_initialiser)  
	
	def video_feed(self):           
		if self.connect.video_ready:
			try:
				frame = self.vs.read()  #read the next frame                    
				##resize the image
				if self.video_frame.winfo_width()>1:    
					if self.video_frame.winfo_height() < int((self.video_frame.winfo_width()*0.5625)): 
						frame = imutils.resize(frame 
								,width=int(self.video_frame.winfo_height()*1.77777) #image width
								,height=self.video_frame.winfo_height()#image height
								)                               
					else:
						frame = imutils.resize(frame
								,width=self.video_frame.winfo_width()   #image width
								,height=int((self.video_frame.winfo_width()*0.5625))#image height 
								)                                         
				##process the raw frame
				cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA) #colours picture correctly              
				current_image = Image.fromarray(cvimage)        #Something to do with PIL, processes the matrix array                   
				imagetk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
				self.video_frame.imgtk = imagetk  # stops garbage collection            
				self.video_frame.config(image=imagetk)  # show the image in image_box
			except:
					pass
					
		else:   
				#print("should be setting video window to the video not there image")
				self.vid_dis_raw_img = Image.open(self.vid_dis_img_path)
				if self.vid_dis_raw_img.width != self.video_frame.winfo_width():
					self.vid_dis_raw_img = self.vid_dis_raw_img.resize((self.video_frame.winfo_width(),self.video_frame.winfo_height()), Image.ANTIALIAS)
				self.vid_dis_img = ImageTk.PhotoImage(self.vid_dis_raw_img)                     
				self.video_frame.config(image=self.vid_dis_img)                 
		self.master.after(50, self.video_feed)# cause the function to be called after X milliseconds			
	
	def switch_handler(self):		
		if data_send['control_status'] == 'Manual':			
			if self.connect.ssh_ready:
				try:
					file = self.ftp_client.open(config['data_exchange_file'],'w')
					file.close()
					file.open()
					file.seek(0)
					file.truncate()
					file.write(data_send)
					file.close()
					
				except (paramiko.ssh_exception, socket.error) as msg:
					pass
					
		else:
			data_send['control_status'] = 'Manual'
			if self.connect.ssh_ready:
				file = self.ftp_client.open(config['data_exchange_file'],'w')
				file.close()
				file.open()
				file.seek(0)
				file.truncate()
				file.write(data_send)
				file.close()

	def fullscreen(self,event=None):
		if event.char == 'f' or event.num == 1 or event.keysym == 'Escape':
			if self.fullscreen_status == False and (event.char == 'f' or event.num == 1):                                   
				self.frame1.grid(columnspan = 2,rowspan=2)
				self.frame1.lift()      
				self.fullscreen_status = True                   
			else:
				self.frame1.grid(columnspan = 1,rowspan=1)
				self.fullscreen_status = False   

	def event_handler(self,event=None):             
		if event.char == 'f' or event.keysym == 'Escape' or event.num == 1:
			self.fullscreen(event)  
		if event.char == 'q':
			pass 
                
#Opening resolution - height,width    
res = (int(config['resolution_width']),int(config['resolution_height']))

if __name__ == '__main__':
        #create tkinter root
        root = Tk()
        #create instance of app class
        app = App(root,res)     
        root.mainloop()