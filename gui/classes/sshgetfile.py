import time
import threading
import subprocess
from platform import system as system_name  
from subprocess import call as system_call 
import paramiko
import socket


class SSHGetFile():
	def __init__(self): 
		self.file_exists = False
		
	def move_file(self,remote,local):
		if app.connect.ssh_ready:                         
			try:  				
				app.connect.ftp_client.get(remote,local)				
				self.file_exists = True
			except (Exception, paramiko.ssh_exception.AuthenticationException, socket.error) as msg:
				print("error when trying to get {0}: {1}".format(remote,str(msg)))
								
			if self.file_exists: 
				try:
					modified_time = self.connect.ftp_client.stat(remote).st_mtime 
					return modified_time
				except Exception as msg:
					return False					
					# self.depthmap_modified_time = False
					# self.depthmap_file_exists = False