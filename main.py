# Basic imports
import os, struct, array
import subprocess
import time
import datetime

# Motor imports
#from dual_mc33926_rpi import motors, MAX_SPEED

# Manual movement import 
import bin.controller as controller

# Autonomous movement imports
import bin.autonomous as auto

# Depthmap imports
import tensorflow as tf
import bin.depthmap as depthmap
import lib.fcrn.tensorflow.models as fcrn_model

########################################################################

print('Starting tf')

# Tensorflow variables 
width = 640
height = 360
channels = 3
batch = 1
#model_path = '/home/pi/Devel/secbot/lib/fcrn/models/NYU_FCRN.ckpt'
model_path = r'C:\Coding\Secbot\lib\fcrn\models\NYU_FCRN.ckpt'

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

# Warmup Tensorflow
for x in range(1, 10):
    print('{0} run'.format(x))
    depthmap.depthmap_func(network, session, input_placeholder)

print('Done!')


