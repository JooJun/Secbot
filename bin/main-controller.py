import os, struct, array
from fcntl import ioctl
from dual_mc33926_rpi import motors, MAX_SPEED

# Store the states
axis_states = {}

# These constants were borrowed from linux/input.h
axis_names = {	
	0x01 : 'leftstick',
	0x05 : 'rightstick'
}

axis_map = []

# Open the joystick device.
try:
	fn = '/dev/input/js0'
	jsdev = open(fn, 'rb') 
except:
	raise SystemExit("Playstation controller not found")
	
# Get the device name.
buf = bytearray(63)
buf = array.array('b', [ord('\0')] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tostring()

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

try:
	motors.enable()
	motors.setSpeeds(0, 0)
	
	for axis in buf[:num_axes]:
		axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
		axis_map.append(axis_name)
		axis_states[axis_name] = 0
		
	# Main event loop
	while True:
		evbuf = jsdev.read(8)
		if evbuf:
			time, value, type, number = struct.unpack('IhBB', evbuf)

			if type & 0x02:
				axis = axis_map[number]
				if axis == "leftstick" or axis == "rightstick":				
					axis_states[axis] = int(value*(480/32767))			
					
		motors.setSpeeds(axis_states['leftstick'], axis_states['rightstick'])	
		#print ("Left stick value {}, Right stick value {}".format(axis_states['leftstick'], axis_states['rightstick']))

#According to the example.py script this should stop the motors even if
#there is an exception of user presses Ctrl-C to kill process

finally:
	motors.setSpeeds(0, 0)
	motors.disable()
	#print("Disabled motors")
