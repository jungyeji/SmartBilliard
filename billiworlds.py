import sys
import os
import cv2
import imutils
import time
import argparse
import numpy as np
import draw_route

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from collections import deque
from imutils.video import VideoStream

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
logo_class = uic.loadUiType("BILLIWORLDS_LOGO.ui")[0]
loading_class = uic.loadUiType("BILLIWORLDS_LOADING.ui")[0]
start_class = uic.loadUiType("BILLIWORLDS_START.ui")[0]
main_class = uic.loadUiType("BILLIWORLDS_MAIN.ui")[0]
guide_class = uic.loadUiType("BILLIWORLDS_GUIDE.ui")[0]

timer1=QTimer()
timer2=QTimer()
timer3=QTimer()
timerStatus = 0
route_data = []

#화면을 띄우는데 사용되는 Class 선언
class LogoClass(QMainWindow, logo_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        timer1.start(3000)
        timer1.timeout.connect(self.next)

    def next(self) :
        self.close()
        myStartWindow.show()
        app.exec_()
        timer1.stop()

class StartClass(QMainWindow, start_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # Start 버튼 클릭 시 button_start_click 함수 연결
        self.start_button.clicked.connect(self.start_button_click)

    # 버튼 클릭 이벤트 메소드
    def start_button_click(self) :
        self.close()
        myLoadingWindow.show()
        timer2.start(3000)
        # 3초 뒤 myLoadingWindow의 next 메소드 연결
        timer2.timeout.connect(myLoadingWindow.next)
        app.exec_()
        
class LoadingClass(QMainWindow, loading_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        
    def next(self) :
        self.close()
        myMainWindow.show()
        app.exec_()
        timer2.stop()

filename=r'camera_demo.mp4'

class GuideClass(QMainWindow, guide_class) :
    def __init__(self) : 
        super().__init__()
        self.setupUi(self)
        self.show_cropped_ROI()


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
                ret, thresh = cv2.threshold(self.frame,5,255,cv2.THRESH_BINARY_INV)
                
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
                        cv2.circle(thresh, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                        cv2.circle(thresh, center_yel, 5, (0, 255, 255), -1)
                
                if len(cnts_red) > 0:
                    c_red = max(cnts_red, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c_red)
                    M = cv2.moments(c_red)
                    center_red = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                    if radius > 10:
                        cv2.circle(thresh, (int(x), int(y)), int(radius), (0, 0, 255), 2)
                        cv2.circle(thresh, center_red, 5, (0, 0, 255), -1)

                if len(cnts_white) > 0:
                    c_white = max(cnts_white, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c_white)
                    M = cv2.moments(c_white)
                    center_white = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                    if radius > 10:
                        cv2.circle(thresh, (int(x), int(y)), int(radius), (255, 255, 255), 2)
                        cv2.circle(thresh, center_white, 5, (255, 255, 255), -1)
 
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

                # #wall collision
                # for i in range(1, len(pts_white)):
                #     if pts_white[i-1] is None or pts_white[i] is None:
                #         continue;
                #     p_white=np.array(pts_white[i])

                #     #90degree
                #     if(p_white[0]==0 and p_white[1]>0):
                #         print("c1",p_white[0], width-radius)
                #     #270degree
                #     elif(p_white[0]==0 and p_white[1]<0):
                #         print("c2",p_white[0],radius)
                #     #0 degree
                #     elif(p_white[0]>0 and p_white[1]==0):
                #         print("c3",length-radius,p_white[1])
                #     #180degree
                #     elif(p_white[0]<0 and p_white[1]==0):
                #         print("c4",radius,p_white[1])
                #     else:
                #         slope=p_white[1]/p_white[0]
                #         if(p_white[0]>=0 and p_white[1]>=0):
                #             y = p_white[1]+(slope)*(length-radius - p_white[0])
                #             x = p_white[0]+(1/slope)*(width-radius - p_white[1])
                #             if(y <= width-radius):
                #                 print("c5",length-radius,y)
                #             elif(x <= length-radius):
                #                 print("c6",x, width-radius)
                #         elif(p_white[0]>=0 and p_white[1]<=0):
                #             y = p_white[1]+(slope)*(radius - p_white[0])
                #             x = p_white[0]+(1/slope)*(radius - p_white[1])
                #             if(y >= radius):
                #                 print("c7",radius,y)
                #             elif(x >= radius):
                #                 print("c8",x, radius)
                #         else:
                #             y = p_white[1]+(slope)*(radius - p_white[0])
                #             x = p_white[0]+(1/slope)*(radius - p_white[1])
                #             if(y >= radius):
                #                 print("c9",radius,y)
                #             elif(x <= length-radius):
                #                 print("c10",x, width-radius)

                
                # show the frame to our screen
                #route_data = draw_route.getRoute()
                global route_data
                route_data = draw_route.getRoute()
                draw_route.draw_line(thresh, route_data)
                cv2.imshow("Frame",thresh)
                #cv2.imshow("Frame", self.frame)

                # Close program with keyboard 'q'
                if cv2.waitKey(1) == ord('q'):
                    cv2.destroyWindow("Frame")
                    break
                


            else:
                pass



class MainClass(QMainWindow, main_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)

        # 카메라 실행 설정
        self.timer_camera = QTimer()
        self.cap = cv2.VideoCapture('camera_demo.mp4')
        self.set_ui()
        self.__flag_work = 0
        self.x =0
        self.count = 0
        
        # 각 버튼 클릭 이벤트와 메소드 연결
        self.ar_guide_start.clicked.connect(self.ar_guide_start_clicked)
        self.projector_on.clicked.connect(self.projector_on_clicked)
        self.open_camera.clicked.connect(self.open_camera_clicked)
        self.timer_camera.timeout.connect(self.show_camera)
        self.other_route.clicked.connect(self.other_route_clicked)

        # Projector On 버튼 hidden 상태 설정
        self.projector_on.hide()
        
    def ar_guide_start_clicked(self) :
        print("ar_guide")
        # 안내 팝업메시지 띄우기
        message = QMessageBox()
        message.setWindowTitle("DB Ready")
        message.setText("Searching!")
        message.exec_()

        # 버튼 hidden/show 설정
        self.ar_guide_start.hide()
        self.projector_on.show()  

        # 화면에 경로 출력
        global route_data
        route_data = draw_route.drawRoute()
        print("####################################################")
        print(route_data)
        
    def projector_on_clicked(self) :
        print("projector_on")
        global route_data
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11")
        print(route_data)
        # guide 화면 띄우기
        myGuideWindow = GuideClass()
        myGuideWindow.show()
        myGuideWindow.repaint()

    # 웹캠 레이아웃 설정 메소드
    def set_ui(self):
        self.__layout_main = QtWidgets.QHBoxLayout()
        self.__layout_fun_button = QtWidgets.QVBoxLayout()
        self.__layout_data_show = QtWidgets.QVBoxLayout()
 
        self.label_move = QtWidgets.QLabel()
 
        self.label_show_camera.setFixedSize(1000, 450)
        self.label_show_camera.move(430,95)
        self.label_show_camera.setAutoFillBackground(False)
 
        self.__layout_fun_button.addWidget(self.open_camera)
        self.__layout_fun_button.addWidget(self.label_move)
 
        self.__layout_main.addLayout(self.__layout_fun_button)
        self.__layout_main.addWidget(self.label_show_camera)
 
        self.setLayout(self.__layout_main)
        self.label_move.raise_()
 
    # 카메라 실행 메소드
    def open_camera_clicked(self):
        if self.timer_camera.isActive() == False:
            flag = 'camera_demo.mp4'
            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"Camera isn't available", buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.timer_camera.start(30)
                self.open_camera.hide()
        else:
            self.timer_camera.stop()
            self.cap.release()
            self.label_show_camera.clear()
 
    # 화면 출력 메소드
    def show_camera(self):
        flag, self.image = self.cap.read()
        show = cv2.resize(self.image, (640, 480))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        show = cv2.flip(show, 1)
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.label_show_camera.setPixmap(QtGui.QPixmap.fromImage(showImage))
        
    def other_route_clicked(self):
        global route_data
        print('clicked!')
        # 안내 팝업메시지 띄우기
        message = QMessageBox()
        message.setWindowTitle("DB Ready")
        message.setText("Searching!")
        message.exec_()

        # 버튼 hidden/show 설정
        self.ar_guide_start.hide()
        self.projector_on.show()  

        # 화면에 경로 출력
        (route_data) = draw_route.drawRoute()


if __name__ == "__main__" :

    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myLogoWindow = LogoClass() 
    myStartWindow = StartClass() 
    myLoadingWindow = LoadingClass()
    myMainWindow = MainClass() 

    #프로그램 화면을 보여주는 코드
    myLogoWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()