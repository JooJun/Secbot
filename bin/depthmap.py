import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

def depthmap_func(network, session, input_node):

    # Path settings
    image_path = '/home/pi/Devel/secbot/depthmaps/cam.jpg'
    #image_path = r'C:\Coding\Secbot\depthmaps\cam.jpg'
    image_output = '/home/pi/Devel/secbot/depthmaps/depth.png'
    #image_output = r'C:\Coding\Secbot\depthmaps\depth.png'

    # Input size
    #height = 360
    height = 216
    #width = 640
    width = 384

    # Read Camera image 
    img = Image.open(image_path)
    img = img.resize([width, height], Image.ANTIALIAS)
    img = np.array(img).astype('float32')
    img = np.expand_dims(np.asarray(img), axis = 0)

    # Evaluate the network
    pred = session.run(network.get_output(), feed_dict={input_node: img})

    # Output the evaluated image
    plt.imsave(image_output, pred[0,:,:,0])
    

