import numpy as np 
import cv2 as cv
from PIL import Image, ImageTk
from imutils.video import FPS, WebcamVideoStream, FileVideoStream 
import imutils  
# Depthmap imports 
import tensorflow as tf 
import bin.depthmap as depthmap 
import lib.fcrn.tensorflow.models as fcrn_model
from timeit import default_timer as timer

width = 640
#width = 384
height = 360
#height = 216
channels = 3
batch = 1
model_path = r'C:\Coding\Secbot\lib\fcrn\models\NYU_FCRN.ckpt'

input_placeholder = tf.placeholder(tf.float32, shape=(None, height, width, channels))             
network = fcrn_model.ResNet50UpProj({'data': input_placeholder}, batch, 1, False)             
session = tf.Session()             
saver = tf.train.Saver()             
saver.restore(session, model_path)

for x in range(1, 10):
    start = timer()
    print('{0} run'.format(x))
    depthmap.depthmap_func(network, session, input_placeholder)
    end = timer()
    print('Time taken {}'.format(end-start))

print('Warmup done')

while True:
    depthmap.depthmap_func(network, session, input_placeholder)
    print('Running main loop')

print('Exiting')


