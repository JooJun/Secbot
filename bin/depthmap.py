import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import cv2 as cv
from imutils.video import FPS, WebcamVideoStream, FileVideoStream

def depthmap_func(network, session, input_node):

    # Path settings
    try:
        #image_path = '/home/pi/Devel/secbot/files/cam.jpg'
        image_path = r'C:\Coding\Secbot\gui\content\depth\cam.jpg'
    except:
        return None

    #image_output = '/home/pi/Devel/secbot/files/depth.png'
    image_output = r'C:\Coding\Secbot\gui\content\depth\depth.png'

    # Input size
    height = 360
    #height = 216
    #height = 108
    width = 640
    #width = 384
    #width = 192

    # Read Camera image 
    img = Image.open(image_path)
    img = img.resize([width,height], Image.ANTIALIAS)
    #img = cv.resize(image_path, dsize=(width, height), interpolation=cv.INTER_CUBIC)
    img = np.array(img).astype('float32')
    img = np.expand_dims(np.asarray(img), axis = 0)

    # Evaluate the network
    pred = session.run(network.get_output(), feed_dict={input_node: img})

    # Output the evaluated image
    plt.imsave(image_output, pred[0,:,:,0], cmap='binary')
    

