from tkinter import *
import newport as nwp
import tkinter as tk
from tkinter.ttk import Separator, Labelframe
import PIL
from PIL import Image,ImageTk
import cv2
import numpy as np
try:
    import tisgrabber as IC
except: None


STEP_FACTOR = 25000

WIDTH = 640
HEIGHT = 480

controller = nwp.Controller(idProduct=0x4000, idVendor=0x104d)


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_widgets()

        # CAMS

        self.cam1_label = Label(self)
        self.cam1_label.grid(row=2, column=1, rowspan=10, columnspan=5)

        self.cam2_label = Label(self)
        self.cam2_label.grid(row=2, column=7, rowspan=10, columnspan=5)

        try:
            self.cap1 = IC.TIS_CAM()
            self.cap1.open('DFK 72BUC02 28910508')
            self.cap1.SetVideoFormat('RGB32 (640x480)')
            self.cap1.SetFrameRate(25.0)
            self.cap1.StartLive(0)
            self.show_cam1_TIS()
        except:
            self.cap1 = cv2.VideoCapture(0)
            self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
            self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
            self.show_cam1_InternalCam()


    def show_cam1_InternalCam(self):
        #capture frame-by-frame
        _, frame = self.cap1.read()
        #our operations on  the frame came here
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #overlay crossair
        cv2image[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
        cv2image[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
        cv2image[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
        cv2image[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]

        #display the resulting frame
        cv2.putText(cv2image, 'CAM 1: Laser Axis', (10,25), 4, .8, (0, 0, 0), thickness=2)
        cv2.putText(cv2image, 'CAM 1: Laser Axis', (10,25), 4, .8, (255, 255, 255), thickness=1)
        image = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=image)
        self.cam1_label.imgtk = imgtk
        self.cam1_label.configure(image=self.cam1_label.imgtk)
        self.cam1_label.after(10, self.show_cam1_InternalCam)

    def show_cam1_TIS(self):
        self.cap1.SnapImage()
        #capture frame-by-frame
        frame = self.cap1.GetImage()
        #our operations on  the frame came here
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #overlay crossair
        cv2image[int(HEIGHT/2),:int(WIDTH/2)-10,:]= [(255,0,0)]
        cv2image[int(HEIGHT/2),int(WIDTH/2)+10:,:]= [(255,0,0)]
        cv2image[:int(HEIGHT/2)-10,int(WIDTH/2),:]= [(255,0,0)]
        cv2image[int(HEIGHT/2)+10:,int(WIDTH/2),:]= [(255,0,0)]

        #display the resulting frame
        cv2.putText(cv2image, 'CAM 1: Laser Axis', (10,25), 4, .8, (0, 0, 0), thickness=2)
        cv2.putText(cv2image, 'CAM 1: Laser Axis', (10,25), 4, .8, (255, 255, 255), thickness=1)
        image = PIL.Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=image)
        self.cam1_label.imgtk = imgtk
        self.cam1_label.configure(image=self.cam1_label.imgtk)
        self.cam1_label.after(10, self.show_cam1_TIS)



    def create_widgets(self):

        # CAM SNAPSHOT

        self.cam1_snap = tk.Button(self, text='SNAP')
        self.cam1_snap['width'] = 10
        self.cam1_snap.grid(row=1,column=1)

        self.cam2_snap = tk.Button(self, text='SNAP')
        self.cam2_snap['width'] = 10
        self.cam2_snap.grid(row=1,column=11)

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

        #self.empty_space = Label(self, text=self.HOIZONTAL_FACTOR2*' ') # 5
        #self.empty_space.grid(row=1,column=11)

        self.empty_space = Label(self, text=5*'\n') # 6
        self.empty_space.grid(row=3,column=6)

        self.empty_space = Label(self, text=5*'\n') # 7
        self.empty_space.grid(row=11,column=6)

        self.empty_space = Label(self, text='\n') # 8
        self.empty_space.grid(row=12,column=1)

        self.empty_space = Label(self, text='\n') # 9
        self.empty_space.grid(row=16,column=1)

        self.empty_space = Label(self, text='\n') # 10
        self.empty_space.grid(row=20,column=1)

        self.empty_space = Label(self, text='\n') # 11
        self.empty_space.grid(row=22,column=1)

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


        ### STOP BUTTON ###

        self.button_stop = tk.Button(self)
        self.button_stop["text"] = "STOP"
        self.button_stop["fg"] = "red"
        self.button_stop['font']='sans 13 bold'
        self.button_stop["command"] =  lambda : controller.command('ST')
        self.button_stop["width"] = 10
        self.button_stop.grid(row=2,column=6)

        ### STATUS INDICATOR ###

        self.motor1_status = tk.IntVar()
        self.motor1_status_label = tk.Label(self, textvariable=self.motor1_status, fg = 'red')
        self.motor1_status.set('')
        self.motor1_status_label.grid(row=15,column=3)

        self.motor2_status = tk.IntVar()
        self.motor2_status_label = tk.Label(self, textvariable=self.motor2_status, fg = 'red')
        self.motor2_status.set('')
        self.motor2_status_label.grid(row=19,column=3)

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

        self.refresh_label()



        ### MOTOR 1 ###

        self.motor1_button_jogging = tk.Button(self)
        self.motor1_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor1_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('1MV-'))
        self.motor1_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor1_button_jogging["width"] = 10
        self.motor1_button_jogging.grid(row=13,column=2, sticky="e")

        self.motor1_button_jogging = tk.Button(self)
        self.motor1_button_jogging["text"] = "\u25B7\u25B7" # >>>
        self.motor1_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('1MV+'))
        self.motor1_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor1_button_jogging["width"] = 10
        self.motor1_button_jogging.grid(row=13,column=4, sticky="w")

        self.motor1_label = tk.Label(self, text='PIEZO 1')
        self.motor1_label.grid(row=13,column=3)

        self.motor1_button = tk.Button(self)
        self.motor1_button["text"] = "\u25C0" # <
        self.motor1_button["command"] = lambda : [controller.command(str('1PR-' + str(self.motor1_entry.get())))]
        self.motor1_button["width"] = 10
        self.motor1_button.grid(row=14,column=2, sticky="e")

        self.motor1_input = tk.IntVar()
        self.motor1_entry = tk.Entry(self, text=self.motor1_input, width=10)
        self.motor1_entry.grid(row=14,column=3)
        self.motor1_entry.focus_force()

        self.motor1_button = tk.Button(self)
        self.motor1_button["text"] = "\u25B6" # >
        self.motor1_button["command"] = lambda : controller.command(str('1PR' + str(self.motor1_entry.get())))
        self.motor1_button["width"] = 10
        self.motor1_button.grid(row=14,column=4, sticky="w")



        ### MOTOR 2 ###

        self.motor2_button_jogging = tk.Button(self)
        self.motor2_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor2_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('2MV-'))
        self.motor2_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor2_button_jogging["width"] = 10
        self.motor2_button_jogging.grid(row=17,column=2, sticky="e")

        self.motor2_button_jogging = tk.Button(self)
        self.motor2_button_jogging["text"] = "\u25B7\u25B7" # >>>
        self.motor2_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('2MV+'))
        self.motor2_button_jogging.bind('<ButtonRelease-1>', lambda event: controller.command('ST'))
        self.motor2_button_jogging["width"] = 10
        self.motor2_button_jogging.grid(row=17,column=4, sticky="w")

        self.motor2_input = tk.IntVar()

        self.motor2_entry = tk.Entry(self, text=self.motor2_input, width=10)
        self.motor2_entry.grid(row=18,column=3)
        self.motor2_entry.focus_force()

        self.motor2_label = tk.Label(self, text='PIEZO 2')
        self.motor2_label.grid(row=17,column=3)

        self.motor2_button = tk.Button(self)
        self.motor2_button["text"] = "\u25C0" # <
        self.motor2_button["command"] = lambda : controller.command(str('2PR-' + str(self.motor2_entry.get())))
        self.motor2_button["width"] = 10
        self.motor2_button.grid(row=18,column=2, sticky="e")


        self.motor2_button = tk.Button(self)
        self.motor2_button["text"] = "\u25B6" # >
        self.motor2_button["command"] = lambda : controller.command(str('2PR' + str(self.motor2_entry.get())))
        self.motor2_button["width"] = 10
        self.motor2_button.grid(row=18,column=4, sticky="w")

        ### MOTOR 3 ###

        self.motor3_button_jogging = tk.Button(self)
        self.motor3_button_jogging["text"] = "\u25C1\u25C1" # <<<
        self.motor3_button_jogging.bind('<ButtonPress-1>', lambda event: controller.command('3MV-'))
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

        self.motor3_label = tk.Label(self, text='PIEZO 3')
        self.motor3_label.grid(row=13,column=9)

        self.motor3_button = tk.Button(self)
        self.motor3_button["text"] = "\u25C0" # <
        self.motor3_button["command"] = lambda : controller.command(str('3PR-' + str(self.motor3_entry.get())))
        self.motor3_button["width"] = 10
        self.motor3_button.grid(row=14,column=8, sticky="e")


        self.motor3_button = tk.Button(self)
        self.motor3_button["text"] = "\u25B6" # >
        self.motor3_button["command"] = lambda : controller.command(str('3PR' + str(self.motor2_entry.get())))
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

        self.motor4_label = tk.Label(self, text='PIEZO 4')
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

        ### MOTOR 5 (STEP MOTOR) ###

        self.motor5_input = tk.IntVar(0)

        self.motor5_entry = tk.Entry(self, text=self.motor5_input, width=10)
        self.motor5_entry.grid(row=18,column=9)
        self.motor5_entry.focus_force()

        self.motor5_label = tk.Label(self, text='STEPPER')
        self.motor5_label.grid(row=17,column=9)




        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "\u25C0 DESK" # <
        self.motor5_button["command"] = lambda : self.subtract()
        self.motor5_button["width"] = 10
        self.motor5_button.grid(row=18,column=8, sticky="e")


        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "DOOR \u25B6" # >
        self.motor5_button["command"] = lambda : self.add()
        self.motor5_button["width"] = 10
        self.motor5_button.grid(row=18,column=10, sticky="w")

        self.motor5_direction_left = StringVar()
        self.motor5_direction_right = StringVar()

        self.motor5_direction_label = tk.Label(self) # left
        self.motor5_direction_label['font'] = 'sans 26'
        self.motor5_direction_label["textvariable"] = self.motor5_direction_left
        self.motor5_direction_label.grid(row=19,column=8, sticky="e")

        self.motor5_direction_label = tk.Label(self) # right
        self.motor5_direction_label['font'] = 'sans 26'
        self.motor5_direction_label["textvariable"] = self.motor5_direction_right
        self.motor5_direction_label.grid(row=19,column=10, sticky="w")

        self.motor5_pos = tk.IntVar(0)
        self.motor5_pos_label = tk.StringVar()
        self.motor5_pos_label.set('0 stp\n0.0 mm')

        self.motor5_status_label = tk.Label(self)
        self.motor5_status_label["textvariable"] = self.motor5_pos_label
        self.motor5_status_label["width"] = 10
        self.motor5_status_label.grid(row=19,column=9)

        self.motor5_button = tk.Button(self)
        self.motor5_button["text"] = "\u2205"
        self.motor5_button["command"] = lambda : [self.motor5_pos.set(0),
                                                    self.motor5_pos_label.set('0 stp\n0.0 mm'),
                                                    self.motor5_direction_right.set(''),
                                                    self.motor5_direction_left.set('')]
        self.motor5_button["width"] = 5
        self.motor5_button.grid(row=17,column=10, sticky="w")


        ### MOTOR 6 (ROTATION) ###

        #self.motor6_label = tk.Label(self, text='ROTATION')
        #self.motor6_label.grid(row=21,column=6)

        self.motor6_button = tk.Button(self)
        self.motor6_button["text"] = '\u21BB' # CW
        #self.motor6_button["command"] = lambda : controller.command(str('4PR' + str(self.motor4_entry.get())))
        self.motor6_button["width"] = 10
        self.motor6_button.grid(row=21,column=5)

        self.motor6_button = tk.Button(self)
        self.motor6_button["text"] = '\u21BA' # CCW
        #self.motor6_button["command"] = lambda : controller.command(str('4PR' + str(self.motor4_entry.get())))
        self.motor6_button["width"] = 10
        self.motor6_button.grid(row=21,column=7)

        self.motor6_input = tk.IntVar()

        self.motor6_entry = tk.Entry(self, text=self.motor6_input, width=10)
        self.motor6_entry.grid(row=21,column=6)
        self.motor6_entry.focus_force()

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

    def subtract(self):
        self.motor5_pos.set(self.motor5_pos.get() - int(self.motor5_input.get()))
        self.motor5_pos_label.set(str(str(abs(self.motor5_pos.get())) + ' stp\n' + str(abs(self.motor5_pos.get() / STEP_FACTOR)) + ' mm'))

        if self.motor5_pos.get() < 0:
            self.motor5_direction_left.set('\u29C0')
            self.motor5_direction_right.set('')
        elif self.motor5_pos.get() == 0:
            self.motor5_direction_left.set('')
            self.motor5_direction_right.set('')
        else:
            self.motor5_direction_left.set('')
            self.motor5_direction_right.set('\u29C1')

    def add(self):
        self.motor5_pos.set(self.motor5_pos.get() + int(self.motor5_input.get()))
        self.motor5_pos_label.set(str(str(abs(self.motor5_pos.get())) + ' stp\n' + str(abs(self.motor5_pos.get() / STEP_FACTOR)) + ' mm'))

        if self.motor5_pos.get() < 0:
            self.motor5_direction_left.set('\u29C0')
            self.motor5_direction_right.set(' ')
        elif self.motor5_pos.get() == 0:
            self.motor5_direction_left.set(' ')
            self.motor5_direction_right.set(' ')
        else:
            self.motor5_direction_left.set(' ')
            self.motor5_direction_right.set('\u29C1')


if __name__ == '__main__':
    root = tk.Tk()
    root.title('xBeam Control')
    #root.geometry('1440x800')
    root.resizable(False, False)

    app = Application(master=root)
    app.mainloop()
