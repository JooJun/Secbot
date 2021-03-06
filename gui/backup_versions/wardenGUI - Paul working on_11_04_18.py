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

#Create config dictionary from file
config = {}
data_send = {}
data_receive = {}

with open("config.txt") as config_file:
	for line in config_file:		
		if not line.strip() == '' and not line.startswith('#'):				
			parts = line.split('=')
			config[parts[0].strip()] = parts[1].strip()

#Video related
import numpy as np
import cv2 as cv
from PIL import Image, ImageTk  
from imutils.video import FPS, WebcamVideoStream, FileVideoStream
import imutils          

class App:
	def __init__(self,master,res): 

		self.pi_ip = config['pi_ip']
		self.cam_ip = config['cam_ip']
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
		
		###frame 3 contains the CONSOLE###
		self.frame3 = Frame(self.master, background="black")
		self.frame3.grid(column = 0, row = 1, sticky='nsew')    
		self.frame3.grid_rowconfigure(0,weight = 1)
		self.frame3.grid_columnconfigure(0,weight = 1)
		# self.frame3.grid_columnconfigure(1,weight = 1)
						
		self.textArea = Text(self.frame3,wrap=WORD, foreground="black", background="white", width=1, height=1, state=DISABLED)          
		self.textArea.grid(sticky='nsew')

		#Scrollbar (not working)
		#self.scroll=Scrollbar(self.textArea, orient = VERTICAL)
		# self.scroll=Scrollbar(self.textArea)
		# self.scroll.grid(column=1, row=0, sticky='nsew')
		# self.textArea.config(yscrollcommand=self.scroll.set)  
		# self.scroll.config(command=self.textArea.yview)                       
		
		self.console_fhandle = False    
		self.console_file_exists = False
		self.console_modified_time = 0
		self.console_file_path = config['console_file_path']	

		###Frame 4 DEPTHMAP###
		self.frame4 = Frame(self.master, background="black")
		self.frame4.grid(column = 1, row = 1, sticky='nsew')    
		self.frame4.grid_rowconfigure(0,weight = 1)
		self.frame4.grid_columnconfigure(0,weight = 1)
		
		self.image_frame = Label(self.frame4,width=self.frame4.winfo_width(),height=self.frame4.winfo_height(),background="black")
		self.image_frame.grid(sticky = 'nsew')
		
		self.img_modified_time = 0
		self.img_file_exists = False
		self.depthmap_img_remote = config['depthmap_file_path_remote'] 
		self.depthmap_img_local = config['content_folder']+config['depthmap_file_path_local'] 
		
		#SSH settings
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())          
		
		#Set variables to check connections
		self.video_conn_ready = False
		self.pi_conn_ready = False
		
		self.video_ready = False                
		self.ssh_ready = False          
		
		#Start threads:-
		
		#Console thread
		self.console_thread = threading.Thread(target=self.write_to_console,args=())
		self.console_thread.daemon = True
		self.console_thread.start()
		
		#Video feed thread
		self.video_feed_thread = Thread(target=self.video_feed,args=())
		self.video_feed_thread.daemon = True
		self.video_feed_thread.start()          
		
		#Video feed initialiser thread
		self.video_feed_init_thread = Thread(target=self.video_feed_initialiser,args=())
		self.video_feed_init_thread.daemon = True
		self.video_feed_init_thread.start()
		
		#Connections ready thread
		self.conn_thread = threading.Thread(target=self.conn_ready,args=())
		self.conn_thread.daemon = True
		self.conn_thread.start()        
		
		#Update the map thread
		self.img_thread = threading.Thread(target=self.image_update,args=())
		self.img_thread.daemon = True
		self.img_thread.start()                 
		
		self.console_list = []
		self.modifiedtime = 0
		
		self.authProblem = False	
		
	def conn_ready(self):                   
		while True:     
			try:
				video = str(subprocess.check_output("ping -n 1 "+self.cam_ip, shell=True))
			except:
				video = ""
			try:
				pi = str(subprocess.check_output("ping -n 1 "+self.pi_ip, shell=True))
			except:
				pi = ''                 
			if 'Reply from '+self.pi_ip in pi:  
				self.pi_conn_ready = True
			else:
				self.pi_conn_ready = False      
				self.ssh_ready = False                          
			if 'Reply from '+self.cam_ip in video:
				#print("ping has been received: ",video)
				self.video_conn_ready = True
			else:
				#print("ping failed, setting video connection and video ready to false")
				self.video_conn_ready = False
				self.video_ready = False                        
			time.sleep(3)
					
	def video_feed_initialiser(self):
		if not self.video_ready:
			#print("video feed initilaiser has recognised that self.video_ready is false")
			if self.video_conn_ready:
				#print("attempting to reconnect the video connection")
				self.vs = WebcamVideoStream(src="rtsp://"+self.cam_ip+":554/user=admin&password=&channel=1&stream=0.sdp?real_stream").start()              
				if str(self.vs.read()) != 'None':       
					#print("setting video_ready to true (self.vs is not none)")
					self.video_ready = True                                 
		self.master.after(1000, self.video_feed_initialiser)    
	 
	def image_update(self):
		if self.img_file_exists == False:
			# # print("ssh ready? = ",self.ssh_ready)
			# # print("File exists marked as false, at the top")
			# self.img_modified_time = 0
			# try:   
				# ssh = self.ssh.exec_command('ls', timeout=5)
			# except Exception as msg:
				# #print (msg)
				# pass
			# if self.ssh_ready == False and self.pi_conn_ready == True:                              
				# if self.authProblem != True:
					# #print("ssh connect called")
					# try:
						# self.ssh.connect(self.pi_ip, username=self.pi_username, password=self.pi_password)
						# connected = True
					# except (paramiko.ssh_exception.AuthenticationException, socket.error) as msg:
						# if str(msg) == 'Authentication failed.':
							# self.authProblem = True
						# self.ssh.close()
						# connected = False                                               
							
					# if connected == True:
						# try:
							# print('sftp')
							# self.ftp_client=self.ssh.open_sftp()
							# print('sftp open')
							# self.ssh_ready = True   

						# except (paramiko.ssh_exception, socket.error) as msg:
							# pass
					# else:                   
						# self.ssh_ready = False                                          

			if self.ssh_ready == True and self.img_file_exists == False:
				# print("ssh ready and file doesnt exist")
				# print("should be attempting to open the file again")                           
				try:                                            
					self.ftp_client.get(self.depthmap_img_remote, self.depthmap_img_local)
					self.img_file_exists = True
					# print ("1")
				except Exception as msg:
					# print(msg)
					pass								
				if self.img_file_exists == True: 
					try:
						self.img_modified_time = self.ftp_client.stat(self.depthmap_img_remote).st_mtime                                            
					except Exception as msg:
						self.img_modified_time = False
						self.img_file_exists = False
								
		if self.img_file_exists:
			self.raw_img = Image.open(self.depthmap_img_local)
			try:
				modified_time = self.ftp_client.stat(self.depthmap_img_remote).st_mtime
				size_img = self.ftp_client.stat(self.depthmap_img_remote).st_size
				#print(size_img)
			except:
				modified_time = False
			if modified_time != self.img_modified_time and size_img != 0:
				try:
					self.ftp_client.get(self.depthmap_img_remote, self.depthmap_img_local)
					self.raw_img = Image.open(self.depthmap_img_local)
					self.img_modified_time = modified_time 
				except Exception as msg:
					self.img_file_exists = False
					pass
			if self.raw_img.width != self.image_frame.winfo_width():
				self.raw_img = Image.open(self.depthmap_img_local)        
				self.raw_img = self.raw_img.resize((self.image_frame.winfo_width(),self.image_frame.winfo_height()), Image.ANTIALIAS)
				self.img = ImageTk.PhotoImage(self.raw_img)             
				self.image_frame.config(image=self.img) 

		self.master.after(1000, self.image_update)
			
	def video_feed(self):           
		if self.video_ready:
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
				if self.vid_dis_raw_img.width != self.image_frame.winfo_width():
					self.vid_dis_raw_img = self.vid_dis_raw_img.resize((self.video_frame.winfo_width(),self.video_frame.winfo_height()), Image.ANTIALIAS)
				self.vid_dis_img = ImageTk.PhotoImage(self.vid_dis_raw_img)                     
				self.video_frame.config(image=self.vid_dis_img)                 
		self.master.after(50, self.video_feed)# cause the function to be called after X milliseconds
			
	def event_handler(self,event=None):             
		if event.char == 'f' or event.keysym == 'Escape' or event.num == 1:
			self.fullscreen(event)  
		if event.char == 'q':
			pass 	
	
	def data_exchange(self):
		pass
	
	def switch_handler(self):		
		if data_send['control_status'] == 'Manual':
			
			if self.ssh_ready:
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
			if self.ssh_ready:
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
					
	def write_to_console(self):
		if self.console_file_exists == False:
			# print("ssh ready? = ",self.ssh_ready)
			# print("File exsists marked as false, at the top")
			self.textArea.config(state=NORMAL)
			self.textArea.delete('1.0', END)
			self.textArea.insert(INSERT,"Waiting for console data")                 
			self.textArea.config(state=DISABLED)
			self.modifiedtime = 0
			self.console_count = 0  
			self.console_list = []  
			try:                    
				ssh = self.ssh.exec_command('ls', timeout=5)
			except Exception as msg:
				#print (msg)
				pass
			if self.ssh_ready == False and self.pi_conn_ready == True:                              
				if self.authProblem != True:
					#print("ssh connect called")
					try:
						self.ssh.connect(self.pi_ip, username=self.pi_username, password=self.pi_password)
						connected = True
					except (paramiko.ssh_exception.AuthenticationException, socket.error) as msg:
					#except (paramiko.SSHException, socket.error) as msg:
						print (msg)
						if str(msg) == 'Authentication failed.':
							self.authProblem = True
						self.ssh.close()
						#pass
						connected = False                                               
							
					if connected == True:
						try:
							self.ftp_client=self.ssh.open_sftp()
							self.ssh_ready = True   

						except (paramiko.ssh_exception, socket.error) as msg:
							# print (msg)
							pass
					else:                   
						self.ssh_ready = False                                          

			if self.ssh_ready == True and self.console_file_exists == False:
				#print("ssh ready and file doesnt exist")
				#print("should be attempting to open the file again")                           
				try:                                            
					self.console_fhandle = self.ftp_client.open(self.console_file_path)
					self.console_file_exists = True
					#print ("1")
				except Exception as msg:
					# print(msg)
					pass
						
				if self.console_file_exists == True:                                                                                    
					self.textArea.config(state=NORMAL)      
					self.textArea.delete('1.0', END)
					self.textArea.config(state=DISABLED)
					try:
						modifiedtime = self.ftp_client.stat(self.console_file_path).st_mtime                                            
					except Exception as msg:
						modifiedtime = False
						self.console_file_exists = False
		
		##################################################################################              
		if self.console_file_exists:
			try:
				modifiedtime = self.ftp_client.stat(self.console_file_path).st_mtime
			except:
				modifiedtime = False
			if modifiedtime:
				if modifiedtime != self.console_modified_time or len(self.console_list) <1:                             
					file_temp = self.console_fhandle.readlines()            
					for item in file_temp:
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
				#print("console file doesnt exist line 330")
				self.console_file_exists = False
		self.master.after(1000, self.write_to_console)          
                
#Opening resolution - height,width    
res = (int(config['resolution_width']),int(config['resolution_height']))

if __name__ == '__main__':
        #create tkinter root
        root = Tk()
        #create instance of app class
        app = App(root,res)     
        root.mainloop()