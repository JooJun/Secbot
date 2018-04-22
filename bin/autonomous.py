import bin.motor as motor
import bin.depthmap as depth
import logging
import numpy as np
import cv2 as cv
import time

log = logging.getLogger(__name__)

def autonomous_func(mode, network, session, input_placeholder):
    avoidance_dict = detection(network, session, input_placeholder)

    while mode == 2:
        avoidance(avoidance_dict)
        avoidance_dict_old = avoidance_dict
        time.sleep(1)
        avoidance_dict = detection(network, session, input_placeholder)


def detection(network, session, input_placeholder):
    # Variables 
    avoidance_dict = {'left': None, 'middle': None, 'right':None}
    img_height = 216
    img_width = 384
    left_line = 128
    right_line = 256
    middle_divide = 108
    top = 0
    bottom = 216
    largest_area = 10000

    # Run depthmap on camera
    #depth.depthmap_func(network, session, input_placeholder)

    # Open image path
    image_path = '/home/pi/Devel/secbot/files/depth.png'
    #image_path = r'C:\Coding\Secwin\files\depth.png'
    image_output = '/home/pi/Devel/secbot/files/contour.png'

    # Open image
    im = cv.imread(image_path)
    im = cv.resize(im, dsize=(img_width, img_height), interpolation=cv.INTER_NEAREST)
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

    # Draw side contours
    cv.line(imgray, (left_line, top), (left_line, bottom), (255,255,255))
    cv.line(imgray, (right_line, top), (right_line, bottom), (255,255,255))

    # Set threshold
    ret, thresh = cv.threshold(imgray, 150, 255, 1)
    img, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    for c in contours:
        area = cv.contourArea(c)
        if area > largest_area:
            # Find moments of contours
            m = cv.moments(c)
            if m['m00'] != 0:
                cx = int(m['m10'] / m['m00'])
                cy = int(m['m01'] / m['m00'])
                bottommostx, bottommosty = tuple(c[c[:,:,1].argmax()][0])
            else:
                cx, cy, bottommostx, bottommosty = 0, 0, 0, 0
            # write centroid of contour 
            xy_tuple = cx, cy, bottommostx, bottommosty, area
            #log.info('Contour : {}'.format(xy_tuple))
            if cx < left_line:
                avoidance_dict['left'] = xy_tuple
                #log.info('Left contour')
            elif left_line < cx < right_line:
                avoidance_dict['middle'] = xy_tuple
                #log.info('Middle contour')
            elif cx > right_line:
                avoidance_dict['right'] = xy_tuple
                #log.info('Right contour')
            else:
                pass

            cv.drawContours(img, [c], -1, (125,125,125), 1)
            cv.circle(img, (cx, cy), 1, (100,100,100), -1) 
            cv.circle(img, (bottommostx, bottommosty), 1, (100,100,100), -1) 
            cv.putText(img, "center", (cx -20, cy -20), cv.FONT_HERSHEY_SIMPLEX, 0.3, (100,100,100), 2)

    cv.imwrite(image_output, img)

    return avoidance_dict


def avoidance(avoidance_dict):
    
    left, middle, right = avoidance_dict['left'], avoidance_dict['middle'], avoidance_dict['right']
    blocked = {'left': False,'middle': False,'right': False}
    
    # Check and write side variables whether blocked or not
    if not left:
        blocked['left'] = True
        log.info('Left completely blocked')
    if not middle:
        blocked['middle'] = True
        log.info('Middle completely blocked')
    if not right:
        blocked['right'] = True
        log.info('Right completely blocked')
    
    # Move forward if not blocked
    if not blocked['middle']:
        motor.move_forward()
        log.info('Middle clear, moving forward')
        return
    
    if blocked['middle']:
        if not blocked['left']:
            motor.turn_left_45()
            log.info('Left side clear, turning left')
            return
        elif not blocked['right']:
            motor.turn_right_45()
            log.info('Right side clear, turning right')
            return
    
    # Everything blocked, check left
    motor.turn_left_90()
    avoidance_dict = detection(network, session, input_placeholder)
    left, middle, right = avoidance_dict['left'], avoidance_dict['middle'], avoidance_dict['right']
    blocked = {'left': False,'middle': False,'right': False}

    if not left:
        blocked['left'] = True
        log.info('Left completely blocked')
    if not middle:
        blocked['middle'] = True
        log.info('Middle completely blocked')
    if not right:
        blocked['right'] = True
        log.info('Right completely blocked')
    
    if not blocked['middle']:
        motor.move_forward()
        log.info('Middle clear, moving forward')
        return
    
    # Left blocked, check right
    motor.turn_right_90()
    motor.turn_right_90()

    avoidance_dict = detection(network, session, input_placeholder)
    left, middle, right = avoidance_dict['left'], avoidance_dict['middle'], avoidance_dict['right']
    blocked = {'left': False,'middle': False,'right': False}

    if not left:
        blocked['left'] = True
        log.info('Left completely blocked')
    if not middle:
        blocked['middle'] = True
        log.info('Middle completely blocked')
    if not right:
        blocked['right'] = True
        log.info('Right completely blocked')
    
    if not blocked['middle']:
        motor.move_forward()
        log.info('Middle clear, moving forward')
        return
    
    # All sides blocked, go back
    motor.turn_right_90()
    return

