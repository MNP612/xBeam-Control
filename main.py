from tkinter import *
import newport as nwp
from pipython import GCSDevice
from pipython.pitools import waitonwalk
import tkinter as tk
from tkinter.ttk import Separator, Labelframe
import PIL
from PIL import Image,ImageTk
import cv2
import time
import numpy as np
import math as m
import serial


LOCATION = "lab"


CAM1 = 'DMK 72BUC02 42614164'
CAM2 = 'DMK 72BUC02 42614201'

STEP_FACTOR = 25000
STEPPER_VELOCITY = "1"
STEPPER_REFRESH_RATE = 2000

WIDTH = 640
HEIGHT = 480

if LOCATION == 'lab':
    IMGAE_PATH = r'C:\Users\Jet Squad\Pictures\Camera Roll/'
    
    # Newport piezos
    controller = nwp.Controller(idProduct=0x4000, idVendor=0x104d)

    # PI Rotation stage
    pidevice = GCSDevice('E-872')
    pidevice.InterfaceSetupDlg(key='sample')

    # Sure motion Stepper
    ser = serial.Serial()
    ser.port = "COM6"
    ser.baudrate = 9600
    ser.bytesize = serial.EIGHTBITS
    ser.parity = serial.PARITY_NONE
    ser.stopbits = serial.STOPBITS_ONE
    ser.timeout= .1
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False
    ser.writeTimeout = 0
    ser.open()         # open the serial port
    ser.write(("VE" + STEPPER_VELOCITY + "\r").encode())
    ser.write(("AC1\r").encode())
    ser.write(("DE1\r").encode())
    ser.write(("SP0\r").encode())
    
elif LOCATION == 'home':
    IMGAE_PATH = '/Users/Marvin/Desktop/'
    None


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

        self.edge_width = IntVar()
        self.left_freeze = IntVar()
        self.right_freeze = IntVar()
        self.X = 0
        
        # CAMERAS

        self.cam1_label = Label(self)
        self.cam1_label.grid(row=2, column=1, rowspan=10, columnspan=5)

        self.cam2_label = Label(self)
        self.cam2_label.grid(row=2, column=7, rowspan=10, columnspan=5)

        if LOCATION == "lab":
            import tisgrabber as IC
            # CAM 1
            self.cap1, self.cap2 = IC.TIS_CAM(), IC.TIS_CAM()
            self.cap1.open(CAM1)
            self.cap1.SetVideoFormat('RGB32 (640x480)')
            self.cap1.SetFrameRate(25.0)
            self.cap1.StartLive(0)

            # CAM 2
            self.cap2.open(CAM2)
            self.cap2.SetVideoFormat('RGB32 (640x480)')
            self.cap2.SetFrameRate(25.0)
            self.cap2.StartLive(0)

            self.show_cam_TIS()
        elif LOCATION == "home":
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
            self.show_cam_Internal()


    def show_cam_TIS(self):
        # CAM 1
        self.cap1.SnapImage()
        #capture frame-by-frame
        frame = self.cap1.GetImage()
        #our operations on  the frame came here
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2image = cv2.flip(cv2image,-1)
        #overlay crossair, edge detector

        if self.edge_detector.get() == True:
            cv2image = cv2.Canny(cv2image,self.edge_detector_input1.get(),self.edge_detector_input2.get())

            edges = np.where(cv2image[int(HEIGHT*.15)] == 255)
            edges = np.append(0,np.append(edges[0],WIDTH))
            self.left_edge = max([x for x in edges if x <= WIDTH/2])
            self.right_edge = min([x for x in edges if x > WIDTH/2])
            self.edge_width.set(abs(self.right_edge - self.left_edge))

            cv2image = cv2.cvtColor(cv2image,cv2.COLOR_GRAY2RGB)
            cv2image[int(HEIGHT*.15)-20:int(HEIGHT*.15)+20,self.left_edge:self.left_edge+2] = [(255,0,0)]
            cv2image[int(HEIGHT*.15)-20:int(HEIGHT*.15)+20:,self.right_edge-2:self.right_edge] = [(255,0,0)]
            
            cv2image[int(HEIGHT*.15)-10:int(HEIGHT*.15)+10,self.left_freeze.get():self.left_freeze.get()+2] = [(0,255,0)]
            cv2image[int(HEIGHT*.15)-10:int(HEIGHT*.15)+10:,self.right_freeze.get()-2:self.right_freeze.get()] = [(0,255,0)]

            cv2.rectangle(cv2image, (390, 0), (640,45), (0,0,0), -1)
            cv2.rectangle(cv2image, (0, 0), (260,45), (0,0,0), -1)
            cv2.rectangle(cv2image, (0, 370), (200,480), (0,0,0), -1)


            cv2.putText(cv2image, 'current width: ' + str(self.edge_width.get()), (10,30), 2, .8, (255, 0, 0), thickness=1)
            cv2.putText(cv2image, 'frozen width: ' + str(self.edge_width_freeze.get()), (395,30), 2, .8, (0, 255, 0), thickness=1)

            cv2.putText(cv2image, 'Angle wrt MB', (10,400), 2, .8, (0, 255, 0), thickness=1)
            cv2.putText(cv2image, "Chip:", (10,430), 2, .8, (0, 255, 0), thickness=1)
            cv2.putText(cv2image, str(self.current_angle.get()), (100,430), 2, .8, (0, 255, 0), thickness=1)
            cv2.putText(cv2image, "Jet:", (10,460), 2, .8, (0, 255, 0), thickness=1)
            cv2.putText(cv2image, str(90-self.current_angle.get()), (100,460), 2, .8, (0, 255, 0), thickness=1)

        else:
            cv2image[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
            cv2image[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
            cv2image[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
            cv2image[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]
            #display the resulting frame
            cv2.putText(cv2image, 'CAM 1: Laser Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (0, 0, 0), thickness=2)
            cv2.putText(cv2image, 'CAM 1: Laser Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (255, 255, 255), thickness=1)
        self.image = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.image)
        self.cam1_label.imgtk = imgtk
        self.cam1_label.configure(image=self.cam1_label.imgtk)
        self.image = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.image)
        self.cam1_label.imgtk = imgtk
        self.cam1_label.configure(image=self.cam1_label.imgtk)

        # CAM 2
        self.cap2.SnapImage()
        #capture frame-by-frame
        frame2 = self.cap2.GetImage()
        #our operations on  the frame came here
        cv2image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        cv2image2 = cv2.flip(cv2image2,0)
        #overlay crossair, edge detector

        if self.edge_detector.get() == True:
            cv2image2 = cv2.Canny(cv2image2,self.edge_detector_input1.get(),self.edge_detector_input2.get())
        else:
            cv2image2[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
            cv2image2[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
            cv2image2[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
            cv2image2[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]
            #display the resulting frame
            cv2.putText(cv2image2, 'CAM 2: Beam Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (0, 0, 0), thickness=2)
            cv2.putText(cv2image2, 'CAM 2: Beam Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (255, 255, 255), thickness=1)
        self.image2 = PIL.Image.fromarray(cv2image2)
        imgtk2 = ImageTk.PhotoImage(image=self.image2)
        self.cam2_label.imgtk = imgtk2
        self.cam2_label.configure(image=self.cam2_label.imgtk)

        # Repeat
        self.cam2_label.after(10, self.show_cam_TIS)

    def show_cam_Internal(self):
        # CAM 1
        #capture frame-by-frame
        _, frame = self.cap.read()
        #our operations on  the frame came here
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        #overlay crossair, edge detector
        self.edge_width = IntVar()
        if self.edge_detector.get() == True:
            cv2image = cv2.Canny(cv2image,self.edge_detector_input1.get(),self.edge_detector_input2.get())

            edges = np.where(cv2image[int(HEIGHT*.1)] == 255)
            edges = np.append(0,np.append(edges[0],WIDTH))
            left_edge = max([x for x in edges if x <= WIDTH/2])
            right_edge = min([x for x in edges if x > WIDTH/2])
            self.edge_width.set(abs(right_edge - left_edge))

            cv2image = cv2.cvtColor(cv2image,cv2.COLOR_GRAY2RGB)
            cv2image[int(HEIGHT*.1)-20:int(HEIGHT*.1)+20,left_edge] = [(255,0,0)]
            cv2image[int(HEIGHT*.1)-20:int(HEIGHT*.1)+20:,right_edge-1] = [(255,0,0)]
            cv2.putText(cv2image, 'current width: ' + str(self.edge_width.get()), (10,25), 2, .6, (255, 0, 0), thickness=1)
            cv2.putText(cv2image, 'frozen width:  ' + str(self.edge_width_freeze.get()), (10,50), 2, .6, (0, 255, 0), thickness=1)

        else:
            cv2image[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
            cv2image[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
            cv2image[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
            cv2image[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]
            #display the resulting frame
            cv2.putText(cv2image, 'CAM 1: Laser Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (0, 0, 0), thickness=2)
            cv2.putText(cv2image, 'CAM 1: Laser Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (255, 255, 255), thickness=1)
        self.image = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.image)
        self.cam1_label.imgtk = imgtk
        self.cam1_label.configure(image=self.cam1_label.imgtk)


        # CAM 2
        frame2 = frame*0
        cv2image2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        #overlay crossair, edge detector

        if self.edge_detector.get() == True:
            cv2image2 = cv2.Canny(cv2image2,100,200)
        else:
            cv2image2[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
            cv2image2[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
            cv2image2[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
            cv2image2[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]

            #display the resulting frame
            cv2.putText(cv2image2, 'CAM 2: Beam Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (0, 0, 0), thickness=2)
            cv2.putText(cv2image2, 'CAM 2: Beam Axis' + 23*' ' + time.strftime('%Y/%m/%d %H:%M:%S'), (10,25), 2, .6, (255, 255, 255), thickness=1)
        self.image2 = PIL.Image.fromarray(cv2image2)
        #self.image2 = PIL.Image.new(mode = "RGB", size = (640, 480))
        imgtk2 = ImageTk.PhotoImage(image=self.image2)
        self.cam2_label.imgtk = imgtk2
        self.cam2_label.configure(image=self.cam2_label.imgtk)
        # Repeat
        self.cam2_label.after(10, self.show_cam_Internal)





    def create_widgets(self):

        # CAM SNAPSHOT
        self.cam1_snap_input = tk.StringVar()
        self.cam1_snap_entry = tk.Entry(self, text=self.cam1_snap_input, width=20)
        self.cam1_snap_entry.grid(row=1,column=1)

        self.cam1_snap = tk.Button(self, text='SNAP')
        self.cam1_snap['command'] = lambda : self.image.save(IMGAE_PATH + time.strftime("%Y%m%d-%H%M%S") + "_CAM1" + self.cam1_snap_input.get() + ".png")
        self.cam1_snap['width'] = 10
        self.cam1_snap.grid(row=0,column=1, sticky="w")

        self.cam2_snap_input = tk.StringVar()
        self.cam2_snap_entry = tk.Entry(self, text=self.cam2_snap_input, width=20)
        self.cam2_snap_entry.grid(row=1,column=11)

        self.cam2_snap = tk.Button(self, text='SNAP')
        self.cam2_snap['command'] = lambda : self.image2.save(IMGAE_PATH + time.strftime("%Y%m%d-%H%M%S") + "_CAM2" + self.cam2_snap_input.get() + ".png")
        self.cam2_snap['width'] = 10
        self.cam2_snap.grid(row=0,column=11, sticky="e")


        # EMPTY SPACES

        #self.HOIZONTAL_FACTOR = 30
        #self.HOIZONTAL_FACTOR2 = 30

        #self.empty_space = Label(self, text=self.HOIZONTAL_FACTOR*' ') # 1
        #self.empty_space.grid(row=1,column=1)

        #self.empty_space = Label(self, text=self.HOIZONTAL_FACTOR*' ') # 2
        #self.empty_space.grid(row=1,column=5)

        self.empty_space = Label(self, text='\n') # 3
        self.empty_space.grid(row=1,column=6)

        #self.empty_space = Label(self, text=self.HOIZONTAL_FACTOR2*' ') # 4
        #self.empty_space.grid(row=1,column=7)

        self.empty_space = Label(self, text='      ') # 5
        #self.empty_space.grid(row=1,column=11)

        self.empty_space = Label(self, text=5*'\n') # 6
        self.empty_space.grid(row=3,column=6)

        self.empty_space = Label(self, text=5*'      \n') # 7
        self.empty_space.grid(row=11,column=6)

        self.empty_space = Label(self, text='\n') # 8
        self.empty_space.grid(row=12,column=1)

        self.empty_space = Label(self, text='\n') # 9
        self.empty_space.grid(row=16,column=1)

        self.empty_space = Label(self, text='\n') # 10
        self.empty_space.grid(row=20,column=1)

        self.empty_space = Label(self, text='\n') # 11
        self.empty_space.grid(row=22,column=1)

        self.empty_space = Label(self, text='\n') # 12
        self.empty_space.grid(row=24,column=1)

        # SEPARATORS

        self.separator = Separator(self, orient='horizontal')
        self.separator.grid(row=12, columnspan=12, sticky=(W,E))

        self.separator = Separator(self, orient='horizontal')
        self.separator.grid(row=16, columnspan=12, sticky=(W,E))

        self.separator = Separator(self, orient='horizontal')
        self.separator.grid(row=20, columnspan=12, sticky=(W,E))

        self.columnconfigure(2, weight=2)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=2)

        self.columnconfigure(8, weight=2)
        self.columnconfigure(9, weight=0)
        self.columnconfigure(10, weight=2)

        ### LABELS ###

        self.motor1_status_label = tk.Label(self, text='CATCHER', font='sans 13 bold', width=15)
        self.motor1_status_label.grid(row=14,column=6)

        self.motor1_status_label = tk.Label(self, text='CATCHER\n& JET', font='sans 13 bold')
        self.motor1_status_label.grid(row=18,column=6)

        self.motor1_status_label = tk.Label(self, text='ROTATION', font='sans 13 bold')
        self.motor1_status_label.grid(row=21,column=6)

        ### STOP BUTTON ###

        self.button_stop = tk.Button(self)
        self.button_stop["text"] = "STOP"
        self.button_stop["fg"] = "red"
        self.button_stop['font']='sans 13 bold'
        self.button_stop["command"] =  lambda : [controller.command('ST')
                                                 , ser.write(('ST\r').encode())
                                                 #, self.motor5_running.set("")
                                                 ]
        self.button_stop["width"] = 10
        self.button_stop.grid(row=2,column=6)

        ### STATUS INDICATOR ###

        self.motor1_status = tk.IntVar()
        self.motor1_status_label = tk.Label(self, textvariable=self.motor1_status, fg = 'red')
        self.motor1_status.set('')
        self.motor1_status_label.grid(row=19,column=3)

        self.motor2_status = tk.IntVar()
        self.motor2_status_label = tk.Label(self, textvariable=self.motor2_status, fg = 'red')
        self.motor2_status.set('')
        self.motor2_status_label.grid(row=15,column=3)

        self.motor3_status = tk.IntVar()
        self.motor3_status_label = tk.Label(self, textvariable=self.motor3_status, fg = 'red')
        self.motor3_status.set('')
        self.motor3_status_label.grid(row=15,column=9)

        self.motor4_status = tk.IntVar()
        self.motor4_status_label = tk.Label(self, textvariable=self.motor4_status, fg = 'red')
        self.motor4_status.set('')
        self.motor4_status_label.grid(row=10,column=6)

        self.motor5_status = tk.IntVar()
        self.motor5_status_label = tk.Label(self, textvariable=self.motor5_status, fg = 'red')
        self.motor5_status.set('')
        self.motor5_status_label.grid(row=17,column=8, sticky='e')

        if LOCATION == 'lab':
            self.refresh_label()
        elif LOCATION == 'home':
            None



        ### MOTOR 2 ###

        self.motor1_button_jogging = tk.Button(self)
        self.motor1_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor1_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('2MV+'))
        self.motor1_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor1_button_jogging["width"] = 10
        self.motor1_button_jogging.grid(row=13,column=2, sticky="e")

        self.motor1_button_jogging = tk.Button(self)
        self.motor1_button_jogging["text"] = "\u25B7\u25B7" # >>>
        self.motor1_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('2MV-'))
        self.motor1_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor1_button_jogging["width"] = 10
        self.motor1_button_jogging.grid(row=13,column=4, sticky="w")

        self.motor1_label = tk.Label(self, text='PIEZO 2', width=15)
        self.motor1_label.grid(row=13,column=3)

        self.motor1_button = tk.Button(self)
        self.motor1_button["text"] = "\u25C0" # <
        self.motor1_button["command"] = lambda : [controller.command(str('2PR' + str(self.motor1_entry.get())))]
        self.motor1_button["width"] = 10
        self.motor1_button.grid(row=14,column=2, sticky="e")

        self.motor1_input = tk.IntVar()
        self.motor1_entry = tk.Entry(self, text=self.motor1_input, width=10)
        self.motor1_entry.grid(row=14,column=3)
        self.motor1_entry.focus_force()

        self.motor1_button = tk.Button(self)
        self.motor1_button["text"] = "\u25B6" # >
        self.motor1_button["command"] = lambda : controller.command(str('2PR-' + str(self.motor1_entry.get())))
        self.motor1_button["width"] = 10
        self.motor1_button.grid(row=14,column=4, sticky="w")



        ### MOTOR 5 ###

        self.motor2_button_jogging = tk.Button(self)
        self.motor2_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor2_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('1MV+'))
        self.motor2_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor2_button_jogging["width"] = 10
        self.motor2_button_jogging.grid(row=17,column=2, sticky="e")

        self.motor2_button_jogging = tk.Button(self)
        self.motor2_button_jogging["text"] = "\u25B7\u25B7" # >>>
        self.motor2_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('1MV-'))
        self.motor2_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor2_button_jogging["width"] = 10
        self.motor2_button_jogging.grid(row=17,column=4, sticky="w")

        self.motor2_input = tk.IntVar()

        self.motor2_entry = tk.Entry(self, text=self.motor2_input, width=10)
        self.motor2_entry.grid(row=18,column=3)
        self.motor2_entry.focus_force()

        self.motor2_label = tk.Label(self, text='PIEZO 5')
        self.motor2_label.grid(row=17,column=3)

        self.motor2_button = tk.Button(self)
        self.motor2_button["text"] = "\u25C0" # <
        self.motor2_button["command"] = lambda : controller.command(str('1PR' + str(self.motor2_entry.get())))
        self.motor2_button["width"] = 10
        self.motor2_button.grid(row=18,column=2, sticky="e")


        self.motor2_button = tk.Button(self)
        self.motor2_button["text"] = "\u25B6" # >
        self.motor2_button["command"] = lambda : controller.command(str('1PR-' + str(self.motor2_entry.get())))
        self.motor2_button["width"] = 10
        self.motor2_button.grid(row=18,column=4, sticky="w")

        ### MOTOR 3 ###

        self.motor3_button_jogging = tk.Button(self)
        self.motor3_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor3_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('3MV+'))
        self.motor3_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor3_button_jogging["width"] = 10
        self.motor3_button_jogging.grid(row=13,column=8, sticky="e")

        self.motor3_button_jogging = tk.Button(self)
        self.motor3_button_jogging["text"] = "\u25B7\u25B7" # >>>
        self.motor3_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('3MV-'))
        self.motor3_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor3_button_jogging["width"] = 10
        self.motor3_button_jogging.grid(row=13,column=10, sticky="w")

        self.motor3_input = tk.IntVar()

        self.motor3_entry = tk.Entry(self, text=self.motor3_input, width=10)
        self.motor3_entry.grid(row=14,column=9)
        self.motor3_entry.focus_force()

        self.motor3_label = tk.Label(self, text='PIEZO 3', width=15)
        self.motor3_label.grid(row=13,column=9)

        self.motor3_button = tk.Button(self)
        self.motor3_button["text"] = "\u25C0" # <
        self.motor3_button["command"] = lambda : controller.command(str('3PR' + str(self.motor3_entry.get())))
        self.motor3_button["width"] = 10
        self.motor3_button.grid(row=14,column=8, sticky="e")


        self.motor3_button = tk.Button(self)
        self.motor3_button["text"] = "\u25B6" # >
        self.motor3_button["command"] = lambda : controller.command(str('3PR-' + str(self.motor3_entry.get())))
        self.motor3_button["width"] = 10
        self.motor3_button.grid(row=14,column=10, sticky="w")


        ### MOTOR 4 ###

        self.motor4_button_jogging = tk.Button(self)
        self.motor4_button_jogging["text"] = "\u25B3\u25B3" # <<<UP>>>
        self.motor4_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('4MV+'))
        self.motor4_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor4_button_jogging["width"] = 10
        self.motor4_button_jogging.grid(row=5,column=6)

        self.motor4_button = tk.Button(self)
        self.motor4_button["text"] = '\u25B2' # UP
        self.motor4_button["command"] = lambda : controller.command(str('4PR' + str(self.motor4_entry.get())))
        self.motor4_button["width"] = 10
        self.motor4_button.grid(row=6,column=6)

        self.motor4_input = tk.IntVar()

        self.motor4_entry = tk.Entry(self, text=self.motor4_input, width=10)
        self.motor4_entry.grid(row=7,column=6)
        self.motor4_entry.focus_force()

        self.motor4_label = tk.Label(self, text='PIEZO 1/4')
        self.motor4_label.grid(row=4,column=6)


        self.motor4_button = tk.Button(self)
        self.motor4_button["text"] = "\u25BC" # DOWN
        self.motor4_button["command"] = lambda : controller.command(str('4PR-' + str(self.motor4_entry.get())))
        self.motor4_button["width"] = 10
        self.motor4_button.grid(row=8,column=6)


        self.motor4_button_jogging = tk.Button(self)
        self.motor4_button_jogging["text"] = "\u25BD\u25BD" # <<<DOWN>>>
        self.motor4_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('4MV-'))
        self.motor4_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor4_button_jogging["width"] = 10
        self.motor4_button_jogging.grid(row=9,column=6)

        ### (STEP MOTOR) ###

        self.motor5_input = tk.IntVar(0)

        self.motor5_entry = tk.Entry(self, text=self.motor5_input, width=10)
        self.motor5_entry.grid(row=18,column=9)
        self.motor5_entry.focus_force()

        self.motor5_label = tk.Label(self, text='STEPPER')
        self.motor5_label.grid(row=17,column=9)




        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "DESK \u25B6" # >
        self.motor5_button["command"] = lambda : [#self.subtract()
                                                  self.send_stepper_cmd("FL" + str(self.motor5_input.get()))
                                                  , self.refresh_label_stepper()]
        self.motor5_button["width"] = 10
        self.motor5_button.grid(row=18,column=10, sticky="w")


        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "\u25C0 DOOR" # <
        self.motor5_button["command"] = lambda : [#self.add()
                                                  self.send_stepper_cmd("FL-" + str(self.motor5_input.get()))
                                                  , self.refresh_label_stepper()]
        self.motor5_button["width"] = 10
        self.motor5_button.grid(row=18,column=8, sticky="e")

        self.motor5_direction_left = StringVar()
        self.motor5_direction_right = StringVar()

        self.motor5_direction_label = tk.Label(self) # left
        self.motor5_direction_label['font'] = 'sans 13 bold'
        self.motor5_direction_label["textvariable"] = self.motor5_direction_left
        self.motor5_direction_label.grid(row=19,column=8, sticky="e")

        self.motor5_direction_label = tk.Label(self) # right
        self.motor5_direction_label['font'] = 'sans 13 bold'
        self.motor5_direction_label["textvariable"] = self.motor5_direction_right
        self.motor5_direction_label.grid(row=19,column=10, sticky="w")

        self.motor5_pos = tk.IntVar(0)
        self.motor5_pos_label = tk.StringVar()
        self.motor5_pos_label.set('0 stp\n0.0 mm')

        self.motor5_running = tk.StringVar()
        self.motor5_running_label = tk.Label(self)
        self.motor5_running_label["textvariable"] = self.motor5_running
        self.motor5_running_label["fg"] = "red"
        self.motor5_running_label.grid(row=17,column=8, sticky="e")

        self.motor5_status_label = tk.Label(self)
        self.motor5_status_label["textvariable"] = self.motor5_pos_label
        self.motor5_status_label["width"] = 10
        self.motor5_status_label.grid(row=19,column=9)

        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "\u2205"
        self.motor5_button["command"] = lambda : [#self.motor5_pos.set(0)
                                                  ser.write(("SP0"+'\r').encode())
                                                  ,self.motor5_pos_label.set('0 stp\n0.0 mm')
                                                  ,self.motor5_direction_right.set('')
                                                  , self.motor5_direction_left.set('')
                                                  ]
        self.motor5_button["width"] = 5
        self.motor5_button.grid(row=17,column=10, sticky="w")


        ### MOTOR 6 (ROTATION) ###

        #self.motor6_label = tk.Label(self, text='ROTATION')
        #self.motor6_label.grid(row=21,column=6)

        self.motor6_input = tk.IntVar()


        self.motor6_button = tk.Button(self)
        self.motor6_button["text"] = '\u21BB' # CW
        self.motor6_button["command"] = lambda : pidevice.OSM(1, self.motor6_input.get())
        self.motor6_button["width"] = 10
        self.motor6_button.grid(row=23,column=5, sticky='e')

        self.motor6_button = tk.Button(self)
        self.motor6_button["text"] = '\u21BA' # CCW
        self.motor6_button["command"] = lambda : pidevice.OSM(1, -self.motor6_input.get())
        self.motor6_button["width"] = 10
        self.motor6_button.grid(row=23,column=7, sticky='w')

        

        self.motor6_entry = tk.Entry(self, text=self.motor6_input, width=10)
        self.motor6_entry.grid(row=23,column=6)
        self.motor6_entry.focus_force()


        # EDGE edge_detector
        self.edge_detector = BooleanVar()
        self.edge_detector.set(False)
        self.button_edge = tk.Button(self)
        self.button_edge["text"] = "EDGE VIEW"
        self.button_edge["command"] =  lambda : self.switch()
        self.button_edge["width"] = 10
        self.button_edge.grid(row=0,column=3)

        self.edge_detector_input1 = Scale(self, from_=0, to=500, orient='horizontal')
        self.edge_detector_input1.set(100)
        self.edge_detector_input1.grid(row=0,column=4, sticky='w')

        self.edge_detector_input2 = Scale(self, from_=0, to=500, orient='horizontal')
        self.edge_detector_input2.set(200)
        self.edge_detector_input2.grid(row=1,column=4, sticky='w')

        self.edge_width_freeze = tk.IntVar()
        self.edge_width_freeze_button = tk.Button(self)
        self.edge_width_freeze_button["text"] = "FREEZE"
        self.edge_width_freeze_button["command"] =  lambda : [self.edge_width_freeze.set(self.edge_width.get()),
                                                                self.left_freeze.set(self.left_edge),
                                                                self.right_freeze.set(self.right_edge),
                                                                self.edge_width_freeze_button.config(fg='green')]
        self.edge_width_freeze_button["width"] = 10
        self.edge_width_freeze_button.grid(row=1,column=3)


        self.edge_width = tk.IntVar()
        self.current_angle = tk.IntVar()
        self.get_current_angle()


        #self.edge_width_goto = tk.IntVar()
        #self.translate_angle()

    def refresh_label(self):
        """ refresh the content of the label every second """
        if controller.command('1MD?')[-1] == '1':
            self.motor1_status.set('')
        else :
            self.motor1_status.set('...running...')

        if controller.command('2MD?')[-1] == '1':
            self.motor2_status.set('')
        else :
            self.motor2_status.set('...running...')

        if controller.command('3MD?')[-1] == '1':
            self.motor3_status.set('')
        else :
            self.motor3_status.set('...running...')

        if controller.command('4MD?')[-1] == '1':
            self.motor4_status.set('')
        else :
            self.motor4_status.set('...running...')
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.after(10, self.refresh_label)

    def refresh_label_stepper(self):
        ser.write(("RS"+'\r').encode())
        out1 = ser.read(15).decode("ascii")
        ser.write(("IP"+'\r').encode())
        out2 = ser.read(15).decode("ascii")[3:-1]
        if "F" in out1:
            self.motor5_running.set(str(int(100*abs(int(out2)-self.X)/self.motor5_input.get())) + "%")
            self.motor5_pos_label.set(str(abs(int(out2)))  + ' stp\n' + str(abs(int(out2)) / STEP_FACTOR) + ' mm')

            if int(out2) < 0:
                self.motor5_direction_left.set('\u29C0')
                self.motor5_direction_right.set('')
            elif int(out2) == 0:
                self.motor5_direction_left.set('')
                self.motor5_direction_right.set('')
            else:
                self.motor5_direction_left.set('')
                self.motor5_direction_right.set('\u29C1')
            
            self.after(STEPPER_REFRESH_RATE,self.refresh_label_stepper)       
            
            
        else:
            self.motor5_running.set("")
            
            self.motor5_pos_label.set(str(abs(int(out2)))  + ' stp\n' + str(abs(int(out2)) / STEP_FACTOR) + ' mm')
            self.X = int(out2)

            if self.X < 0:
                self.motor5_direction_left.set('\u29C0')
                self.motor5_direction_right.set('')
            elif self.X == 0:
                self.motor5_direction_left.set('')
                self.motor5_direction_right.set('')
            else:
                self.motor5_direction_left.set('')
                self.motor5_direction_right.set('\u29C1')

  #  def subtract(self):
        #self.motor5_pos.set(self.motor5_pos.get() - int(self.motor5_input.get()))

        #self.motor5_pos_label.set(str(str(abs(self.motor5_pos.get())) + ' stp\n' + str(abs(self.motor5_pos.get() / STEP_FACTOR)) + ' mm'))

        

       # if self.motor5_pos.get() < 0:
       #    self.motor5_direction_left.set('\u29C0')
       #     self.motor5_direction_right.set('')
       # elif self.motor5_pos.get() == 0:
       #     self.motor5_direction_left.set('')
       #     self.motor5_direction_right.set('')
       # else:
       #     self.motor5_direction_left.set('')
       #     self.motor5_direction_right.set('\u29C1')

        #self.motor5_running.set("...running...")
        #self.after(int(self.motor5_input.get()*STEPPER_RUNNING_FACTOR),lambda : self.motor5_running.set(""))

 #   def add(self):
        
        #self.motor5_pos.set(self.motor5_pos.get() + int(self.motor5_input.get()))
        #self.motor5_pos_label.set(str(str(abs(self.motor5_pos.get())) + ' stp\n' + str(abs(self.motor5_pos.get() / STEP_FACTOR)) + ' mm'))
        
       # if self.motor5_pos.get() < 0:
        #    self.motor5_direction_left.set('\u29C0')
        #    self.motor5_direction_right.set(' ')
        #elif self.motor5_pos.get() == 0:
       #     self.motor5_direction_left.set(' ')
       #     self.motor5_direction_right.set(' ')
       # else:
        #    self.motor5_direction_left.set(' ')
        #    self.motor5_direction_right.set('\u29C1')

        #self.motor5_running.set("...running...")
        #self.after(int(self.motor5_input.get()*STEPPER_RUNNING_FACTOR),lambda : self.motor5_running.set(""))

    def closest(self,lst, K):

     lst = np.asarray(lst)
     idx = (np.abs(lst - K)).argmin()
     return lst[idx]

    def switch(self):
        if self.edge_detector.get() == True:
            self.edge_detector.set(False)
            self.button_edge.config(fg='black')
        else:
            self.edge_detector.set(True)
            self.button_edge.config(fg='green')


    def get_current_angle(self):
        angle = np.arccos(self.edge_width.get()/(self.edge_width_freeze.get()+0.0001))*180/np.pi
        if m.isnan(angle):
            angle = 0.00
        self.current_angle.set(round(angle,1))
        
        self.after(10,self.get_current_angle)

    def send_stepper_cmd(self, cmd):
        ser.write((cmd+'\r').encode())
        ser.flushInput()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('xBeam Control')
    root.resizable(False, False)
    #icon = PhotoImage(file = 'main_logo_windows.png')
    #root.iconphoto(False, icon)

    app = Application(master=root)
    app.mainloop()
