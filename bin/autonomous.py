#import bin.motor as motor
import bin.depthmap as depth
import logging
import numpy as np
import cv2 as cv
import time

log = logging.getLogger(__name__)

def autonomous_func(mode, network, session, input_placeholder):
    avoidance_dict = detection(network, session, input_placeholder) 
    #avoidance(

def detection(network, session, input_placeholder):
    avoidance_dict = {'left': [], 'middle': [], 'right':[]}
    left_line = 128
    right_line = 256
    top = 0
    bottom = 216
    largest_area = 300
    depth.depthmap_func(network, session, input_placeholder)
    image_path = '/home/pi/Devel/secbot/files/depth.png'
    #image_path = r'C:\Coding\Secbot\files\depth.png'
    cv.namedWindow('win', cv.WINDOW_NORMAL)
    im = cv.imread(image_path)
    im = cv.resize(im, dsize=(384, 216), interpolation=cv.INTER_NEAREST)
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    cv.imshow('win', imgray)
    cv.waitKey(0)
    cv.line(imgray, (left_line, top), (left_line, bottom), (255,255,255))
    cv.line(imgray, (right_line, top), (right_line, bottom), (255,255,255))
    cv.imshow('win',imgray)
    cv.waitKey(0)
    ret, thresh = cv.threshold(imgray, 150, 255, 1)
    img, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    cv.imshow('win', img)
    cv.waitKey(0)
     
    for c in contours:
        area = cv.contourArea(c)
        if area > largest_area:
            m = cv.moments(c)
            if m["m00"] != 0:
                cx = int(m["m10"] / m["m00"])
                cy = int(m["m01"] / m["m00"])
                bottommostx, bottommosty = tuple(c[c[:,:,1].argmax()][0])
            else:
                cx, cy, bottommostx, bottommosty = 0, 0, 0, 0
            
            xy_tuple = cx, cy, bottommostx, bottommosty
            if cx < left_line:
                temp_list = avoidance_dict['left']
                temp_list.append(xy_tuple)
                avoidance_dict['left'] = temp_list
            elif left_line < cx < right_line:
                temp_list = avoidance_dict['middle']
                temp_list.append(xy_tuple)
                avoidance_dict['middle'] = temp_list
            elif cx > right_line:
                temp_list = avoidance_dict['right']
                temp_list.append(xy_tuple)
                avoidance_dict['right'] = temp_list
            else:
                pass
            cv.drawContours(img, [c], -1, (125,125,125), 1)
            cv.circle(img, (cx, cy), 1, (100,100,100), -1)
            cv.circle(img, (bottommostx, bottommosty), 1, (100,100,100), -1)
            cv.putText(img, "center", (cx -20, cy -20), cv.FONT_HERSHEY_SIMPLEX, 0.3, (100,100,100), 2)
    cv.imshow('win', img)
    cv.waitKey(0)

    return avoidance_dict


def avoidance(objects_list):
    left, front, right = avoidance_dict['left'], avoidance_dict['middle'], avoidance_dict['right']
    blocked = [False,False,False]
   
    # Check if one side is completely blocked
    if not left:
        log.info('Left side blocked')
        blocked[0] = True
    elif not middle:
        log.info('Middle blocked')
        blocked[1] = True
    else not right:
        log.info('Right side blocked')
        blocked[2] = True





