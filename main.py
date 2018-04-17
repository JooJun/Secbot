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

# Depthmap imports
import tensorflow as tf
import bin.depthmap as depthmap
import lib.fcrn.tensorflow.models as fcrn_model

# Open and clear log file
if os.path.exists('files/main.log'):
    open('files/main.log', 'w').close()

# Setup program primitives
mode = 1
logging.basicConfig(filename='files/main.log', level=logging.DEBUG)

########################################################################
logging.info('Set up...')

logging.info('Warming up...')
start = timer()

# Tensorflow variables 
#width = 640
width = 384
#height = 360
height = 216
channels = 3
batch = 1
model_path = '/home/pi/Devel/secbot/lib/fcrn/models/NYU_FCRN.ckpt'
#model_path = r'C:\Coding\Secbot\lib\fcrn\models\NYU_FCRN.ckpt'

# Initializing Tensorflow and run startups
# Placeholder for input image
input_placeholder = tf.placeholder(tf.float32, shape=(None, height, width, channels))

# Construct network
network = fcrn_model.ResNet50UpProj({'data': input_placeholder}, batch, 1, False)

# Start tensorflow session
session = tf.Session()

# Start tensorflow checkpoint 
saver = tf.train.Saver()
saver.restore(session, model_path)

end = timer()
logging.info('Time taken -tf : {}'.format(end-start))

# Warmup Tensorflow
for x in range(1, 10):
    start = timer()
    logging.info('{0} run'.format(x))
    depthmap.depthmap_func(network, session, input_placeholder)
    end = timer()
    logging.info('Time taken -cam : {}'.format(end-start))

logging.info('Warming up... Done!')

while mode:

    if mode == 1:
        logging.info('Starting manual control...')
        mode = controller.controller_func(mode)

    if mode == 2:
        logging.info('Starting autonomous control...')
        mode = auto.autonomous_func(mode, network, session, input_placeholder)

    if not mode:
        break

logging.info('Exiting program...')
