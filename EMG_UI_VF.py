import serial, sys, time, random
import threading as Thrd
import numpy as np
import serial.tools.list_ports as sp
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

#변수 선언
line = []
ui_form = uic.loadUiType("C:\Users\where\OneDrive - 건양대학교\대학관련\과제 자료\3학년 1학기\3학년 1학기 설계 심화1\pycode\EMG_UI.ui")[0]

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self):
        fig = Figure()
        self.axes = fig.add_subplot(211) #RMS
        self.axes2 = fig.add_subplot(212) #MVIC
        super(MplCanvas, self).__init__(fig)
            
class phui(QDialog, ui_form):
    def __init__(self): #UI설정
        global port, rate

        super(phui, self).__init__()
        self.setupUi(self)    

        #버튼 클릭 시 실행될 함수 지정
        self.startButton.clicked.connect(self.startButton_click) 
        self.portButton.clicked.connect(self.portButton_click)

        #RateBox 인수 추가 (아두이노 보드레이트)
        self.RateBox.addItem('2400')
        self.RateBox.addItem('4800')
        self.RateBox.addItem('9600')
        self.RateBox.addItem('19200')
        self.RateBox.addItem('38400')

        #사용하고 있는 포트 불러오기
        list = sp.comports()
        connected = []

        for i in list:
            connected.append(i.device)
            print("Connected COM ports: " + str(connected))

        #포트 선택 콤보박스
        for i in range(0, len(connected)): 
            self.PortBox.addItem(connected[i])
        
        connected.clear()

        #그래프 설정, 레이아웃 설정
        self.sc = MplCanvas()
        toolbar = NavigationToolbar(self.sc, self)
        layout = QVBoxLayout()  
        layout.addWidget(toolbar)
        layout.addStretch(6)
        layout.addWidget(self.sc)

        self.setLayout(layout)
        self.setGeometry(100, 300, 727, 650) #창 출력 위치(100,300), 사이즈(727, 650)
        self.show()

        

    #포트 재탐색 버튼
    def portButton_click(self):
        self.PortBox.clear()

        #사용하고 있는 포트 불러오기
        list = sp.comports()
        connected = []

        for i in list:
            connected.append(i.device)
            print("Connected COM ports: " + str(connected))

        #포트 선택 콤보박스
        for i in range(0, len(connected)): 
            self.PortBox.addItem(connected[i])

        connected.clear()

    #통신시작 버튼     
    def startButton_click(self):
        def a_data(): #아두이노에서 센서값 받아오기
            i = 0
            j = 0
            num = 30 #한번에 불러올 데이터 크기
            line = []
            before_n = []
            lstR = [] #넘파이 배열
            lstX = [] #시간축
            lstY = [] #RMS
            lstY2 = [] #MVIC

            port = self.PortBox.currentText()
            rate = self.RateBox.currentText() #문자열
            int(rate) #정수형으로 형변환
      
            ser = serial.Serial(port, rate, timeout=1)  # 아두이노 통신 설정
            print("아두이노와 통신 시작")

            time.sleep(2) #공백방지 딜레이
            
            #데이터 받아오기
            while True:
                for i in range (num): #num에 저장된 횟수만큼 반복하여 넘파이 배열을 만듬
                    #time.sleep(0.01)
                    line.append(ser.readline().decode("utf-8"))
                    strline = line[i]
                    strline = strline.split(',')
                    
                    before_n[i] = list(map(int, before_n[i]))

                    lstR = before_n    
                    lstR = np.array(lstR)

                    lstX = lstR[:,0]
                    lstX[i] = lstX[i]/1000.0

                #마지막 요소(오류 데이터) 제외
                lstX = lstR[:num-1,0] #시간축
                lstY = lstR[:num-1,1] #RMS
                lstY2 = lstR[:num-1,2] #MVIC

                #데이터 확인용
                print(line[i])
                print(strline)
                print(before_n)
                print(lstR)
                print(type(lstR))
                print(lstX)
                print(lstY)
                
                #while문 50번 반복 마다 그래프 창 클리어
                if(j == 50):
                    self.sc.axes.cla()
                    self.sc.axes2.cla()
                    j = 0

                #다음 데이터 받아오기 위한 변수 초기화
                line = [] 
                lstR = [] 
                before_n = []
                j += 1

                #그래프 그리기
                #RMS 그래프(파란색)
                self.sc.axes.plot(lstX, lstY, color = 'blue', lw = 1)
                self.sc.axes.set_xlabel("time")
                self.sc.axes.set_ylabel("RMS")
                self.sc.axes.grid()

                #MVIC 그래프(빨간색)
                self.sc.axes2.plot(lstX, lstY2, color = 'red', lw = 1)
                self.sc.axes2.set_xlabel("time")
                self.sc.axes2.set_ylabel("MVIC")
                self.sc.axes2.grid()
                self.sc.draw()
              
        #멀티 스레드 사용(센서값 받기)
        th_data = Thrd.Thread(target=a_data) #스레드에서 실행할 함수 지정
        th_data.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = phui()
    myWindow.show()
    app.exec_()