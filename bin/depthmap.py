import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import cv2 as cv
from imutils.video import FPS, WebcamVideoStream, FileVideoStream

def depthmap_func(network, session, input_node):

    # Path settings
    try:
        image_path = video_feed()
        while not image_path:
            image_path = video_feed()
        #image_path = '/home/pi/Devel/secbot/files/cam.jpg'
        #image_path = r'C:\Coding\Secwin\files\cam.jpg'
    except:
        return None

    image_output = '/home/pi/Devel/secbot/files/depth.png'
    #image_output = r'C:\Coding\Secwin\files\depth.png'

    # Input size
    #height = 360
    height = 216
    #width = 640
    width = 384

    # Read Camera image 
    img = cv.resize(image_path, dsize=(width, height), interpolation=cv.INTER_CUBIC)
    img = np.array(img).astype('float32')
    img = np.expand_dims(np.asarray(img), axis = 0)

    # Evaluate the network
    pred = session.run(network.get_output(), feed_dict={input_node: img})

    # Output the evaluated image
    plt.imsave(image_output, pred[0,:,:,0], cmap='binary')
    
def conn_video():
    try:
        video = str(subprocess.check_output('ping -n 1 192.168.1.10', shell=True))
    except:
        video = ''
    if 'Reply from 192.168.1.10' in video:
        video_conn_ready = True
    else:
        video_conn_ready = False
    
def video_feed_initialiser():
    video_conn_ready = conn_video()
    if video_conn_ready:
        vs = WebcamVideoStream(src='rtsp://192.168.1.10:554/user=admin&password=&channel=1&stream=0.sdp?real_stream').start()
        if str(vs.read()) != 'None':
            video_ready = True
        else:
            video_ready = False
        return video_ready, vs
    else:
        video_ready = False
        return video_ready, None

def video_feed():
    video_ready, vs = video_feed_initializer()
    while not video_ready:
        video_ready, vs = video_feed_initializer()
    if video_ready and vs:
        try:
            frame = vs.read()
            cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
            return cvimage
        except:
            return None
    else:
        return None
