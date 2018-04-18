from dual_mc33926_rpi import motors, MAX_SPEED
import time

speed_f = MAX_SPEED - 280
speed_b = -(MAX_SPEED - 280)

def move_enable():
    motors.enable()

def move_disable():
    motors.disable()

def move_forward():
    motors.setSpeeds(speed_f, speed_f)

def move_backwards():
    motors.setSpeeds(speed_b, speed_b)

def turn_left_45():
    motors.setSpeeds(speed_b, speed_f)
    time.sleep(0.5)

def turn_left_90():
    motors.setSpeeds(speed_b, speed_f)
    time.sleep(1)

def turn_left_135():
    motors.setSpeeds(speed_b, speed_f)
    time.sleep(1.5)

def turn_right_45():
    motors.setSpeeds(speed_f, speed_b)
    time.sleep(0.5)

def turn_right_90():
    motors.setSpeeds(speed_f, speed_b)
    time.sleep(1)

def turn_right_135():
    motors.setSpeeds(speed_f, speed_b)
    time.sleep(1.5)

