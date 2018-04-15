import time
import queue, threading
import subprocess
from platform import system as system_name  
from subprocess import call as system_call 
import paramiko
import socket

class Connect:
	def __init__(self,config):	
	###initialise variables
		#ip address, username and password for pi taken from the config dictionary
		self.cam_ip = config['cam_ip']
		self.pi_ip = config['pi_ip']
		self.pi_username = config['pi_username']
		self.pi_password = config['pi_password']
		
		#set the connections being ready to false
		self.pi_conn_ready = False	
		self.video_conn_ready = False
		self.video_ready = False

		#ssh variables initialise
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
		self.ssh.load_system_host_keys()
		self.ls = False
		self.ssh_connecting = False
		self.sftp_check = False			
		self.authProblem = False
		self.ssh_ready = False
		
		#Connections ready thread
		self.conn_thread = threading.Thread(target=self.conn_ready,args=())
		self.conn_thread.daemon = True
		self.conn_thread.start() 
		
	def conn_ready(self): 
			while True: 
				ssh = False
				try:
					video = str(subprocess.check_output("ping -n 1 "+self.cam_ip, shell=True))
				except Exception as msg:
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
					self.video_conn_ready = True
				else:					
					self.video_conn_ready = False
					self.video_ready = False  
				self.ls = False
				try:                    
					self.ls = self.ssh.exec_command('ls', timeout=5)
				except Exception as msg:
					self.ssh_ready = False	
					if not self.ssh_connecting:
						self.ssh_connect()				
				time.sleep(1)	
		
	# Function makes the initial connection with username and password and 
	# initialises the self.ftp_client which is used for sftp
	def ssh_connect(self):	
		self.ssh_connecting = True
		if self.ssh_ready == False and self.pi_conn_ready == True:                              
			if self.authProblem != True:
				try:		
					self.console_list = []
					self.ssh.connect(self.pi_ip, username=self.pi_username, password=self.pi_password)
					self.ftp_client=self.ssh.open_sftp()					
					self.ssh_ready = True				
				except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException, socket.error) as msg:	
					#Sets authProblem to true if something failed with authorisation
					if str(msg) == 'Authentication failed.':
						self.authProblem = True
					self.ssh_ready = False
					self.ssh.close()				
		self.ssh_connecting = False	

	#Function moves the files via SFTP, if modified time is different	
	def get_file(self,remote,local,modified_time):
		file_data = {}		
		if self.ssh_ready: 
			try:
				file_data['modified_time'] = self.ftp_client.stat(remote).st_mtime
				file_data['file_size'] = self.ftp_client.stat(remote).st_size
				file_data['file_exists'] = True
			except (Exception, paramiko.ssh_exception.AuthenticationException, socket.error) as msg:
				file_data['file_exists'] = False
				file_data['modified_time'] = 0
				#print(msg)				
			if file_data['modified_time'] != modified_time:
				try:	
					self.ftp_client.get(remote,local)				
					file_data['file_exists'] = True			
				except (Exception, paramiko.ssh_exception.AuthenticationException, socket.error) as msg:
					#print("error when trying to get {0}: {1}".format(remote,str(msg)))
					file_data['file_exists'] = False
					file_data['modified_time'] = 0
			return file_data
			
	def put_file(self,local,remote):
		if self.ssh_ready:
			try:
				self.ftp_client.get(local,remote)
				return True
			except:
				return False

	def get_file_lines(self,remote):
		file_data = {}		
		if self.ssh_ready: 			
			try:
				fhandle = self.ftp_client.open(remote,'r')
				list = fhandle.readlines()				
				fhandle.close()
				return list
			except (Exception, paramiko.ssh_exception.AuthenticationException, socket.error, IOError) as msg:
				print("error when trying to open {0}: {1}".format(remote,str(msg)))
				return False
		else:
			return False