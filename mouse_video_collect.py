from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

filename='test.mp4'

class staticROI(object):
    def __init__(self):
        self.capture = cv2.VideoCapture(filename)

        # Bounding box reference points and boolean if we are extracting coordinates
        self.image_coordinates = []
        self.extract = False
        self.selected_ROI = False

        self.update()

    def update(self):
        while True:
            if self.capture.isOpened():
                # Read frame
                (self.status, self.frame) = self.capture.read()
                ########
                #self.frame = cv2.flip(self.frame,1)
                #self.frame = cv2.flip(self.frame,0)
                ########
                cv2.imshow('image', self.frame)
                time.sleep(0.1)
                key = cv2.waitKey(2)



                # Crop image
                if key == ord('c'):
                    self.clone = self.frame.copy()
                    cv2.namedWindow('image')
                    cv2.setMouseCallback('image', self.extract_coordinates)
                    while True:
                        key = cv2.waitKey(2)
                        cv2.imshow('image', self.clone)

                        # Crop and display cropped image
                        if key == ord('c'):
                            self.crop_ROI()
                            break

                if key == ord('d'):
                    self.clone = self.frame.copy()
                    cv2.namedWindow('image')
                    cv2.setMouseCallback('image', self.extract_coordinates)
                    while True:
                        key = cv2.waitKey(2)
                        cv2.imshow('image',self.clone)

                        if key == ord('d'):
                            self.get_point()
                            break

                # Close program with keyboard 'q'
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    #self.show_cropped_ROI()
                    exit(1)
            else:
                pass

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            self.extract = False

            self.selected_ROI = True

            # Draw rectangle around ROI
            cv2.rectangle(self.clone, self.image_coordinates[0], self.image_coordinates[1], (0,255,0), 2)

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.frame.copy()
            self.selected_ROI = False

    def crop_ROI(self):
        if self.selected_ROI:
            self.cropped_image = self.frame.copy()

            x1 = self.image_coordinates[0][0]
            y1 = self.image_coordinates[0][1]
            x2 = self.image_coordinates[1][0]
            y2 = self.image_coordinates[1][1]
            self.x1 = x1
            self.x2 = x2
            self.y1 = y1
            self.y2 = y2
            self.cropped_image = self.cropped_image[y1:y2, x1:x2]

            print('Cropped image: {} {}'.format(self.image_coordinates[0], self.image_coordinates[1]))
        else:
            print('Select ROI to crop before cropping')

    def get_point(self):
        x_range = self.x2 - self.x1
        y_range = self.y2 - self.y1

        if self.selected_ROI:
            x = (self.image_coordinates[0][0]-self.x1)*800/x_range
            y = (self.image_coordinates[0][1]-self.y1)*400/y_range

            print('Ball Point: {} {}'.format(int(x),int(y)))


    def show_cropped_ROI(self):
        #cv2.imshow('cropped image', self.cropped_image)
        self.capture = cv2.VideoCapture(filename)
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video", help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
        args = vars(ap.parse_args())

        yellowLower = (0,80,100)
        yellowUpper = (40, 255, 255)
        pts_yel = deque(maxlen=args["buffer"])

        redLower = (-10,150,50)
        redUpper = (10,255, 255)
        pts_red = deque(maxlen=args["buffer"])

        whiteLower = (0,0,0)
        whiteUpper = (255,50, 255)
        pts_white = deque(maxlen=args["buffer"])
        while True:
            if self.capture.isOpened():
                # Read frame
                (self.status, self.frame) = self.capture.read()

                x1 = self.image_coordinates[0][0]
                y1 = self.image_coordinates[0][1]
                x2 = self.image_coordinates[1][0]
                y2 = self.image_coordinates[1][1]
                self.frame = self.frame[y1:y2, x1:x2]
                length = x2-x1
                width = y2-y1
                #time.sleep(0.005)
                #cv2.imshow('image', self.frame)
                 # resize the frame, blur it, and convert it to the HSV
                # color space
                #self.frame = imutils.resize(self.frame, width=600)
                blurred = cv2.GaussianBlur(self.frame, (11, 11), 0)
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                # construct a mask for the color "green", then perform
                # a series of dilations and erosions to remove any small
                # blobs left in the mask
         
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
                        cv2.circle(self.frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                        cv2.circle(self.frame, center_yel, 5, (0, 255, 255), -1)
                
                if len(cnts_red) > 0:
                    c_red = max(cnts_red, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c_red)
                    M = cv2.moments(c_red)
                    center_red = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                    if radius > 10:
                        cv2.circle(self.frame, (int(x), int(y)), int(radius), (0, 0, 255), 2)
                        cv2.circle(self.frame, center_red, 5, (0, 0, 255), -1)

                if len(cnts_white) > 0:
                    c_white = max(cnts_white, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c_white)
                    M = cv2.moments(c_white)
                    center_white = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                    if radius > 10:
                        cv2.circle(self.frame, (int(x), int(y)), int(radius), (255, 255, 255), 2)
                        cv2.circle(self.frame, center_white, 5, (255, 255, 255), -1)
 
                #update the points queue
                pts_yel.appendleft(center_yel)
                pts_red.appendleft(center_red)
                pts_white.appendleft(center_white)

                #loop over the set of tracked points
                for i in range(1, len(pts_white)):
                    #if either of the tracked points are None, ignore them
                    if pts_yel[i-1] is None or pts_yel[i] is None:
                        continue
                    if pts_red[i-1] is None or pts_red[i] is None:
                        continue
                    if pts_white[i-1] is None or pts_white[i] is None:
                        continue
                    p_yel=np.array(pts_yel[i])
                    p_red=np.array(pts_red[i])
                    p_white=np.array(pts_white[i])

                    dist_yel_white=np.sqrt(np.sum((p_yel-p_white)**2))
                    dist_white_red=np.sqrt(np.sum((p_white-p_red)**2))
                    ##ball collision
                    if(dist_yel_white<=2*radius):
                        print("white/yellow", p_white, p_yel)   
                    if(dist_white_red<=2*radius):
                        print("white/red", p_white, p_red)   

                #wall collision
                for i in range(1, len(pts_white)):
                    if pts_white[i-1] is None or pts_white[i] is None:
                        continue;
                    p_white=np.array(pts_white[i])

                    #90degree
                    if(p_white[0]==0 and p_white[1]>0):
                        print("c1",p_white[0], width-radius)
                    #270degree
                    elif(p_white[0]==0 and p_white[1]<0):
                        print("c2",p_white[0],radius)
                    #0 degree
                    elif(p_white[0]>0 and p_white[1]==0):
                        print("c3",length-radius,p_white[1])
                    #180degree
                    elif(p_white[0]<0 and p_white[1]==0):
                        print("c4",radius,p_white[1])
                    else:
                        slope=p_white[1]/p_white[0]
                        if(p_white[0]>=0 and p_white[1]>=0):
                            y = p_white[1]+(slope)*(length-radius - p_white[0])
                            x = p_white[0]+(1/slope)*(width-radius - p_white[1])
                            if(y <= width-radius):
                                print("c5",length-radius,y)
                            elif(x <= length-radius):
                                print("c6",x, width-radius)
                        elif(p_white[0]>=0 and p_white[1]<=0):
                            y = p_white[1]+(slope)*(radius - p_white[0])
                            x = p_white[0]+(1/slope)*(radius - p_white[1])
                            if(y >= radius):
                                print("c7",radius,y)
                            elif(x >= radius):
                                print("c8",x, radius)
                        else:
                            y = p_white[1]+(slope)*(radius - p_white[0])
                            x = p_white[0]+(1/slope)*(radius - p_white[1])
                            if(y >= radius):
                                print("c9",radius,y)
                            elif(x <= length-radius):
                                print("c10",x, width-radius)
                    
                # show the frame to our screen
                cv2.imshow("Frame", self.frame)

                key = cv2.waitKey(2)
                # Close program with keyboard 'q'
                if key == ord('q'):
                    cv2.destroyAllWindows()
                    exit(1)


            else:
                pass


if __name__ == '__main__':
    static_ROI = staticROI()