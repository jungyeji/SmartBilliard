import findDB
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

capture = cv2.VideoCapture('camera_demo.mp4')
(status, frame) = capture.read()
def convert_data(data, white_x, white_y, red_x, red_y) : 
    col = deque()
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    #print(width, height)
    
    white_x = 606*width/800     #606
    white_y = 341*height/400    #341
    tempCol = (white_x, white_y)
    col.append(tempCol)

    for x in data :
        real_x = x[0][0]*width/800
        real_y = x[0][1]*height/400
        tempCol = (real_x, real_y)
        
        col.append(tempCol)

    red_x = red_x*width/800
    red_y = red_y*height/400
    tempCol = (red_x, red_y)
    col.append(tempCol)

    return col

def draw_line(canvas, data) :
    tempData = data[0]
    for i in range(1, len(data)) :
        cv2.line(canvas, (int(tempData[0]), int(tempData[1])), (int(data[i][0]), int(data[i][1])), (255, 0, 0), 5)
        tempData = data[i]

def drawRoute() :    
    newFrame = cv2.copyMakeBorder(frame, 0,0,0,0,cv2.BORDER_REPLICATE)
    (route_data, yel_x, yel_y, red_x, red_y, white_x, white_y) = findDB.find_DB()
    (converted_data) = convert_data(route_data, white_x, white_y, red_x, red_y)
    draw_line(newFrame, converted_data)
    cv2.imshow("result", newFrame)
    cv2.waitKey(0)
    return converted_data

def getRoute() :
    (route_data, yel_x, yel_y, red_x, red_y, white_x, white_y) = findDB.find_DB_AR()
    (converted_data) = convert_data(route_data, white_x, white_y, red_x, red_y)
    return converted_data

if __name__ == "__main__" :
    newFrame = cv2.copyMakeBorder(frame, 0, 0, 0, 0, cv2.BORDER_REPLICATE)
    (route_data, yel_x, yel_y, red_x, red_y, white_x, white_y) = findDB.find_DB()
    (converted_data) = convert_data(route_data, white_x, white_y, red_x, red_y)
    draw_line(newFrame, converted_data)

    cv2.imshow("result", newFrame)
    cv2.waitKey(0)
    #draw_line(converted_data)
