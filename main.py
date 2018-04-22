# Basic imports
import os, struct, array
import subprocess
import time
import datetime
from timeit import default_timer as timer
import logging

# Motor imports
from dual_mc33926_rpi import motors, MAX_SPEED

# Manual movement import 
import bin.controller as controller

# Autonomous movement imports
import bin.autonomous as auto

# Open and clear log file
if os.path.exists('files/main.log'):
    open('files/main.log', 'w').close()

# Setup program primitives
mode = 2
logging.basicConfig(filename='files/main.log', level=logging.DEBUG)

########################################################################
logging.info('Set up...')

while mode:

    if mode == 1:
        logging.info('Starting manual control...')
        mode = controller.controller_func(mode)

    if mode == 2:
        logging.info('Starting autonomous control...')
        mode = auto.autonomous_func(mode)

    if not mode:
        break

logging.info('Exiting program...')
