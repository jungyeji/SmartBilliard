from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

def find_ball():
    capture = cv2.VideoCapture('camera_demo.mp4')
    
    (status, frame) = capture.read()
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    yellowLower = (0,80,100)
    yellowUpper = (40, 255, 255)

    redLower = (-10,150,50)
    redUpper = (10,255, 255)

    whiteLower = (0,0,0)
    whiteUpper = (255,50, 255)
    if capture.isOpened():
        # Read frame
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        mask_yel = cv2.inRange(hsv, yellowLower, yellowUpper)
        mask_yel = cv2.erode(mask_yel, None, iterations=2)
        mask_yel = cv2.dilate(mask_yel, None, iterations=2)

        mask_red = cv2.inRange(hsv, redLower, redUpper)
        mask_red = cv2.erode(mask_red, None, iterations=2)
        mask_red = cv2.dilate(mask_red, None, iterations=2)

        mask_white = cv2.inRange(hsv, whiteLower, whiteUpper)
        mask_white = cv2.erode(mask_white, None, iterations=2)
        mask_white = cv2.dilate(mask_white, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts_yel = cv2.findContours(mask_yel.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_yel = imutils.grab_contours(cnts_yel)
        center_yel = None

        cnts_red = cv2.findContours(mask_red.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_red = imutils.grab_contours(cnts_red)
        center_red = None
        
        cnts_white = cv2.findContours(mask_white.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts_white = imutils.grab_contours(cnts_white)
        center_white = None
        # only proceed if at least one contour was found
        if len(cnts_yel) > 0:
            c_yel = max(cnts_yel, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c_yel)
            M = cv2.moments(c_yel) 
            center_yel = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center_yel, 5, (0, 255, 255), -1)
        
        if len(cnts_red) > 0:
            c_red = max(cnts_red, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c_red)
            M = cv2.moments(c_red)
            center_red = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)
                cv2.circle(frame, center_red, 5, (0, 0, 255), -1)

        if len(cnts_white) > 0:
            c_white = max(cnts_white, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c_white)
            M = cv2.moments(c_white)
            center_white = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
                cv2.circle(frame, center_white, 5, (255, 255, 255), -1)


        yel_x = int(center_yel[0]*800/width)
        yel_y = int(center_yel[1]*400/height)
        red_x = int(center_red[0]*800/width)
        red_y = int(center_red[1]*400/height)
        white_x = int(center_white[0]*800/width)
        white_y = int(center_white[1]*400/height)

        return yel_x, yel_y, red_x, red_y, white_x, white_y

        cv2.imshow("Frame", frame)

    else:
        pass