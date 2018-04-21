#system
import os
import time
import datetime
import threading
from platform import system as system_name  
from subprocess import call as system_call 
from threading import Thread
import subprocess
from multiprocessing import Process

#ssh/sftp
import paramiko
import socket

#tkinter
from tkinter import *#, ttk from tkinter import ttk
import tkinter as tk
import tkinter.scrolledtext as tkst

#Video related imports
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk  
from imutils.video import FPS, WebcamVideoStream, FileVideoStream
import imutils

#Own classes
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

class App:
	def __init__(self,master,res): 
		#Grab the camera ip from config
		self.cam_ip = config['cam_ip']
		
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
		self.master.grid_columnconfigure(0, weight=40)           
		self.master.grid_columnconfigure(1, weight=28)

		self.master.grid_propagate(False)
		
		#Set the opening resolution, and minsize if required
		#self.master.minsize(res[1],res[0])                             
		self.master.geometry(str(res[1])+"x"+str(res[0]))
		
	#####Set 4 frames and put them into the grid (grid contains 4 equal boxes)#####
	###############################################################################
	
	###Frame 1 will hold the VIDEO STREAM###
		self.frame1 = Frame(self.master)
		self.frame1.grid(column = 0, row = 0, sticky='nsew')
		self.frame1.grid_rowconfigure(0,weight = 1)
		self.frame1.grid_columnconfigure(0,weight = 1)		
		
		#create video frame within frame1, i.e. a tkinter Label
		self.video_frame = Label(self.frame1,width=self.frame1.winfo_width(),height=self.frame1.winfo_height(),background="white", relief=RIDGE)
		#Label 'sticks' to top, bottom, left and right
		self.video_frame.grid(sticky='nsew')
		
		#bind double mouse click to the video frame
		self.video_frame.bind('<Double-Button>', self.event_handler)
		
		#Picture to display when no video present
		self.vid_dis_img_path = '{0}/vid_disconnect.jpg'.format(config['content_folder'])
		#initialise as default image to show
		self.vid_show_image = Image.open(self.vid_dis_img_path)
		
		self.vid_ratio = [16,9]
		
	###Frame 2 SWITCH / CONTROL PANEL SECTION###			
		self.frame2 = Frame(self.master, background='black')
		self.frame2.grid(column = 1, row = 0,sticky='nsew')
		self.frame2.grid_rowconfigure(0,weight = 1)
		self.frame2.grid_columnconfigure(0,weight = 1)
		
		self.switchpanel_ratio = [16,9]					
		
		#auto switch picture
		self.auto_img_raw = Image.open('{0}/auto_button.png'.format(config['content_folder']))		
		self.auto_photo = ImageTk.PhotoImage(self.auto_img_raw)
		
		#manual switch picture
		self.manual_img_raw = Image.open('{0}/manual_button.png'.format(config['content_folder']))	
		self.manual_photo = ImageTk.PhotoImage(self.manual_img_raw)	

		#self.switch = tk.Button(self.switch_canvas,width=1,height=1,command=self.switch_handler,relief=FLAT,activebackground='black')
		self.switch = tk.Button(self.frame2,width=1,height=1,command=self.switch_handler,relief=FLAT,activebackground='black')
		self.switch.configure(command=self.switch_handler)
		self.switch.grid()
		self.switch.configure(image=self.manual_photo,bg='black')
		
		#initialise the control_status
		data_send["control_status"] = "manual"
		data_receive["control_status"] = "manual"
			
		#data file remote and local paths, (datafile used only by the switch but could be expanded at a later date)
		self.data_local = config['content_folder']+"/"+config['data_local']
		self.data_remote = config['data_remote']
		
	###frame 3 contains the CONSOLE### 
		self.frame3 = Frame(self.master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')    
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
				
		#Create text area with scrollbar within frame 3
		self.textArea = tkst.ScrolledText(self.frame3,wrap=WORD, foreground="black", background="white", width=-1, height=-1, state=DISABLED)          
		self.textArea.grid(sticky='nsew')
   
		#initilaise console variables
		self.console_file_exists = False
		self.console_list = []
		self.console_modified_time = 0
		
		#Set the console local and remote paths
		self.console_remote = config['console_remote']	
		self.console_local = config['content_folder']+"/"+config['console_local']

	###Frame 4 DEPTHMAP###
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')    
		self.frame4.grid_rowconfigure(0,weight = 1)
		self.frame4.grid_columnconfigure(0,weight = 1)
		
		self.depthmap_frame = Label(self.frame4,width=self.frame4.winfo_width(),height=self.frame4.winfo_height(),background="white", relief=RIDGE)
		self.depthmap_frame.grid(sticky = 'nsew')		
		
		self.depthmap_modified_time = 0
		self.depthmap_file_exists = False
		self.depthmap_img_remote = config['depthmap_file_path_remote'] 
		self.depthmap_img_local = './'+config['content_folder']+config['depthmap_file_path_local'] 
		
		self.depthmap_dis_img_path = '{0}/depmap_disconnect.jpg'.format(config['content_folder'])
		self.depthmap_show_image = Image.open(self.depthmap_dis_img_path)	
		
		self.depthmap_ratio = [16,9]
		
		#delete local data/log files
		try:
			os.remove(self.depthmap_img_local)
			os.remove(self.console_local)
		except:
			pass
	##create instance of other classes
		self.connect = Connect(config)		
		
	#Start functions/threads:-	
		self.write_to_console()
		
		#self.depmap_update()
		# #Update the console thread
		# self.console_thread = threading.Thread(target=self.write_to_console,args=())
		# self.console_thread.daemon = True
		# self.console_thread.start()
		
		#Update the depthmap thread
		self.depmap_thread = threading.Thread(target=self.depmap_update,args=())
		self.depmap_thread.daemon = True
		self.depmap_thread.start()  
		
		# #Video feed thread
		self.video_feed_thread = Thread(target=self.video_feed,args=())
		self.video_feed_thread.daemon = True
		self.video_feed_thread.start() 
		
		# # #Video feed thread attempt with multiprocess
		# self.video_feed_thread = Process(group=None,name='vid_feed',target=self.video_feed,args=())
		# self.video_feed_thread.daemon = True
		# self.video_feed_thread.start() 
			
		#Video feed initialiser thread
		self.video_feed_init_thread = Thread(target=self.video_feed_initialiser,args=())
		self.video_feed_init_thread.daemon = True
		self.video_feed_init_thread.start()	
		
		#draw thread
		self.draw_thread = Thread(target=self.draw,args=())
		self.draw_thread.daemon = True
		self.draw_thread.start()	
	
	###Class functions###################################################
	
	def resize(self,image,frame,ratio):
		if frame.winfo_width()>1:    
			if frame.winfo_height() < int((frame.winfo_width()*(ratio[1]/ratio[0]))):
				image = image.resize((int(frame.winfo_height()*(ratio[0]/ratio[1])),frame.winfo_height()),Image.ANTIALIAS)                               
			else:
				image = image.resize((frame.winfo_width(),int(frame.winfo_width()*(ratio[1]/ratio[0]))),Image.ANTIALIAS)  							
			return image
		else:	
			return image
	
	def draw(self):	
		self.draw_list = [{
						'exists':self.depthmap_file_exists
						,'frame':self.depthmap_frame
						,'image':self.depthmap_show_image
						,'disconnect_image':self.depthmap_dis_img_path
						,'ratio':self.depthmap_ratio
						}]

		#loops through and draw each item in the list
		for item in self.draw_list:
			if (item['image'].width != item['frame'].winfo_width()) or (item['image'].height != item['frame'].winfo_height()):
				if not item['exists']:					
					item['image'] = Image.open(item['disconnect_image'])						
				self.temp_draw_image = self.resize(item['image'],item['frame'],item['ratio'])		
				item['image'] = ImageTk.PhotoImage(self.temp_draw_image)					
			item['frame'].config(image=item['image'])
			
		#Drawing and resizing the button 			
			self.switch.configure(height=self.frame2.winfo_height()/5,width=self.frame2.winfo_width()/3)
			if data_receive["control_status"] == "manual" and self.frame2.winfo_height()>1:
				self.manual_img_raw = Image.open('{0}/manual_button.png'.format(config['content_folder']))
				self.manual_img_raw = self.manual_img_raw.resize((int(self.frame2.winfo_width()/3),int(self.frame2.winfo_height()/5)),Image.ANTIALIAS)		
				self.manual_photo = ImageTk.PhotoImage(self.manual_img_raw)
				self.switch.configure(image=self.manual_photo)
			elif self.frame2.winfo_height()>1:
				self.auto_img_raw = Image.open('{0}/auto_button.png'.format(config['content_folder']))
				self.auto_img_raw = self.auto_img_raw.resize((int(self.frame2.winfo_width()/3),int(self.frame2.winfo_height()/5)),Image.ANTIALIAS)		
				self.auto_photo = ImageTk.PhotoImage(self.auto_img_raw)
				self.switch.configure(image=self.auto_photo)
								
		self.switch.grid()
		
		self.master.after(100,self.draw)
	
	def depmap_update(self):
		file_data = self.connect.get_file(self.depthmap_img_remote,self.depthmap_img_local,self.depthmap_modified_time)
		if file_data != None:
			if file_data['file_exists']:
				self.depthmap_frame.configure(bg='black')
				if file_data['modified_time'] != self.depthmap_modified_time and file_data['file_size'] != 0:
					self.depthmap_modified_time = file_data['modified_time']	
				self.depthmap_file_exists = True		
			try:
				self.depthmap_show_image = Image.open(self.depthmap_img_local)
			except:
				self.depthmap_file_exists = False	
				self.depthmap_frame.configure(bg='white')
		self.master.after(1000, self.depmap_update)	
		
	def write_to_console(self):	
		file_data = self.connect.get_file(self.console_remote,self.console_local,self.console_modified_time)
		if file_data and file_data['file_exists']:
			file = open(self.console_local).readlines()
			self.console_modified_time = file_data['modified_time']	
			file_length = len(file)				
			#Restrict to only printing tailing 100 lines				
			if file_length > 100:
				file = file[file_length-101:len(file)]
			#Print lines to the text area
			try:
				self.textArea.config(state=NORMAL)
				self.textArea.delete(1.0, END)
				self.textArea.config(state=DISABLED)
				for item in file:	
					self.textArea.config(state=NORMAL)
					self.textArea.insert(END,item)
					self.textArea.config(state=DISABLED)					
				self.textArea.see("end")	

			except Exception as msg:
				print ("Exception in console printing: "+str(msg))				
		else:
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")                 
			self.textArea.config(state=DISABLED)
			self.console_modifiedtime = 0
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
			self.video_frame.configure(bg='black')
			try:
				frame = self.vs.read()  #read the next frame
			    #(frame, cv.COLOR_BGR2RGBA) #colours picture correctly              
				cvimage = cv.cvtColor(frame, cv.COLOR_BGRA2RGB) #colours picture correctly			
				#self.vid_show_image = Image.fromarray(cvimage)#PIL, processes the matrix array 
				current_image = Image.fromarray(cvimage)        #Something to do with PIL, processes the matrix array                   
				imagetk = ImageTk.PhotoImage(image=current_image)  # convert image for tkinter
				self.video_frame.imgtk = imagetk  # stops garbage collection            
				self.video_frame.config(image=imagetk)  # show the image in image_box
			except:
				self.video_frame.configure(bg='white')	
			
		else:
			self.vid_dis_raw_img = Image.open(self.vid_dis_img_path)
			if (self.vid_dis_raw_img.width != self.video_frame.winfo_width()) or (self.vid_dis_raw_img.height != self.video_frame.winfo_height()):
				self.vid_dis_raw_img = self.resize(self.vid_dis_raw_img,self.video_frame,self.vid_ratio)
			self.vid_dis_img = ImageTk.PhotoImage(self.vid_dis_raw_img)                     
			self.video_frame.config(image=self.vid_dis_img)     
		self.master.after(100, self.video_feed)# cause the function to be called after X milliseconds	
			
	def switch_handler(self):	
		if self.connect.ssh_ready:
			if data_send["control_status"] == "manual":				
				#self.switch.configure(image=self.auto_photo)
				data_send["control_status"] = "automatic"
			else:
				#self.switch.configure(image=self.manual_photo)
				data_send["control_status"] = "manual"				
			#open/create the data file locally and get handle
			try:
				file = open(self.data_local,'w')
			except IOError:				
				file = open(self.data_local, 'w+')			
	
			#Empty the file
			file.seek(0)
			file.truncate()
			#print the contents of the dictionary to lines such as control_status=manual
			for k,v in data_send.items():
				file.write("{0}={1}".format(k,v))
				file.write("\n")
			file.close()
			
			#send the data
			try:
				#put the file to the remote location
				self.connect.put_file(self.data_local,self.data_remote)
				
				#read the raw remote data from file
				remote_data = self.connect.get_file_lines(self.data_remote)
				
				#put the remote data from remote file into data_receive dictionary
				for item in remote_data:
					parts = item.split('=')					
					data_receive[parts[0].strip()] = parts[1].strip()	
				
			except Exception as msg:
				print(msg)		
			
			#final check makes sure that what is in the remote location is reflected locally
			if data_receive['control_status'] != data_send['control_status']:
					if data_receive['control_status'] == 'manual':
						data_send['control_status'] = data_receive['control_status']
						#self.switch.configure(image=self.manual_photo)						
					if data_receive['control_status'] == 'automatic':
						data_send['control_status'] = data_receive['control_status']
						#self.switch.configure(image=self.auto_photo)	
						
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