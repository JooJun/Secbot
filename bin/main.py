import os, struct, array
from fcntl import ioctl
from dual_mc33926_rpi import motors, MAX_SPEED
import subprocess
import time
count = 0

# Create dictionary to store the axis states
axis_states = {}
button_states = {}
#axis map creation
axis_map = []
button_map = []

ratio = 480/32767

#Creating a dictionary of axis names, allows the use of easy labels such as 'leftstick'
axis_names = {	
	0x01 : 'leftstick',
	0x05 : 'rightstick'
	# 0x05 : 'rightstick'
}

button_names = {
	0x13c : 'psbutton'	
}

jsdev = False
while not jsdev:
	try:
		fn = '/dev/input/js0'
		jsdev = open(fn, 'rb')
	except:
		pass

# Get the device name.
buf = array.array('b', [ord('\0')] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tostring()

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

buf = array.array('B', [0])
ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
num_buttons = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

for axis in buf[:num_axes]:
		axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
		axis_map.append(axis_name)
		axis_states[axis_name] = 0

# # Get the button map.
buf = array.array('H', [0] * 200)
ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

for btn in buf[:num_buttons]:
	btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
	button_map.append(btn_name)
	button_states[btn_name] = 0

try:	
	motors.enable()
	motors.setSpeeds(0, 0)

	# Main event loop
	while True:
		evbuf = jsdev.read(8)
		if evbuf:
			time, value, type, number = struct.unpack('IhBB', evbuf)
			if number == 16 and value ==1:
				bluetooth = subprocess.Popen(["bluetoothctl"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
				bluetooth.stdin.write(b"disconnect 00:1B:FB:21:14:98")
				bluetooth.stdin.flush()
				output, errors = bluetooth.communicate()
				motors.setSpeeds(0, 0)
				#print(output,errors)
				#print("ps logo pressed",value)	
				jsdev = False
				while not jsdev:
					try:
						fn = '/dev/input/js0'
						jsdev = open(fn, 'rb')	
						count=0
					except:
						pass	
			if type:				
				#print (type, value, number)
				axis = axis_map[number]
				if axis == "leftstick" or axis == "rightstick":	
					if count>5:
						axis = axis_map[number]
						axis_states[axis] = int(value*ratio)	
						#print ("Left stick value {}, Right stick value {}".format(axis_states['leftstick'], axis_states['rightstick']))
					count+=1
		motors.setSpeeds(axis_states['leftstick'], axis_states['rightstick'])			

#Stop the motors if there is an exception of user presses Ctrl-C to kill process

finally:
	motors.setSpeeds(0, 0)
	motors.disable()
	#print("Disabled motors")