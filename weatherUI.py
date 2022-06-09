#!/usr/bin/env python

##
# UI
# #

import tkinter as tk
from PIL import Image, ImageTk
import subprocess

BACKGROUND_COLOR = "#101012"
FOREGROUND_COLOR = "#adadad"

class WeatherUI(tk.Tk) :
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen",True)
        self.title("Pi Weather Station")
        # self.configure(background='')
        self.bind("<Double-Button-1>", self.exit)
        self.bind("<Button-1>", self.turn_on_video_output) # to turn off video_output, we use cron table 

        self.room = {
            "title": tk.StringVar(self, "Room"),
            "temperature": tk.StringVar(self, "---- °C "),
            "humidity": tk.StringVar(self, "---- %"),
            "pressure": tk.StringVar(self, "----")
        }
        self.outside = {
            "title": tk.StringVar(self, "Outside"),
            "temperature": tk.StringVar(self, "---- °C "),
            "humidity": tk.StringVar(self, "---- %"),
            "wind": tk.StringVar(self, "---- N")
        }

        self.time = {
            "hour": tk.StringVar(self, "00:00:00"),
            "date": tk.StringVar(self, "1 Jan"),
        }
        self.weather = {
            "description": tk.StringVar(self, "----"),
            "air_quality": tk.StringVar(self, "Air: :-)")
        }

        ##
        # The GUI use those canvas:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 
        #                               pictCanvas
        # 
        # - - - - - - - - - - - - - - - bottomCanvas- - - - - - - - - - - - - - -
        # blCanvas           bmlCanvas            bmrCanvas              brCanvas
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # #
        #---------------------------------------------------------------
        self.imageBackground = Image.open('icons/background.jpg')
        self.imageIcon = Image.open("icons/10d@2x.png")
       
        self.initBackground()
        self.initUI()
        
    def initBackground(self):
        
        pictCanvas = tk.Canvas(self,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        pictCanvas.pack(fill=tk.BOTH, expand=1)
        pictCanvas.update()

        img_w, img_h = self.imageBackground.size
        width_factor = pictCanvas.winfo_width() / img_w
        height_factor = pictCanvas.winfo_height() / img_h
        factor = min(width_factor, height_factor)
        self.imageBackground = self.imageBackground.resize((int(img_w*factor) , int(img_h*factor)))
        self.imagePhotoBackground = ImageTk.PhotoImage(self.imageBackground)
        
        label0 = tk.Label(pictCanvas, image=self.imagePhotoBackground, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        label0.pack()


    def initUI(self):
        bottomCanvas = tk.Canvas(self,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        bottomCanvas.pack(anchor=tk.S, fill=tk.X)

        blCanvas = tk.Canvas(bottomCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        blCanvas.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.init_roomUI(blCanvas)
        
        brCanvas = tk.Canvas(bottomCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        brCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.init_outsideUI(brCanvas)
        
        bmtlCanvas = tk.Canvas(bottomCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        bmtlCanvas.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.initMiddleLeft(bmtlCanvas)

        bmrCanvas = tk.Canvas(bottomCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        bmrCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.initMiddleRight(bmrCanvas)

    def init_roomUI(self, master) :
        titleLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["title"], font=("Helvetica", 15,"bold"))
        titleLabel.pack(anchor=tk.NW)
        temperatureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["temperature"], font=("Helvetica", 30,"bold"))
        temperatureLabel.pack(side=tk.LEFT)
        humidityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["humidity"], font=("Helvetica", 15,"bold"))
        humidityLabel.pack(anchor=tk.SW)
        pressureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["pressure"], font=("Helvetica", 15,"bold"))
        pressureLabel.pack(side=tk.LEFT)

    def init_outsideUI(self, master) :
        titleLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["title"], font=("Helvetica", 15,"bold"))
        titleLabel.pack(anchor=tk.NE)
        temperatureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["temperature"], font=("Helvetica", 30,"bold"))
        temperatureLabel.pack(side=tk.RIGHT)
        humidityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["humidity"], font=("Helvetica", 15,"bold"))
        humidityLabel.pack(anchor=tk.SE)
        windLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["wind"], font=("Helvetica", 15,"bold"))
        windLabel.pack(anchor=tk.SE)

    def initMiddleRight(self, master) :
        detailCanvas = tk.Canvas(master, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        detailCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)

        descriptionLabel = tk.Label(detailCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.weather["description"], font=("Helvetica", 15,"bold"))
        descriptionLabel.pack()

        airQualityLabel = tk.Label(detailCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.weather["air_quality"], font=("Helvetica", 12,"bold"))
        airQualityLabel.pack()
        
        self.imageIcon = self.imageIcon.resize((100,100))
        self.imagePhoto = ImageTk.PhotoImage(self.imageIcon)

        iconCanvas = tk.Canvas(master, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        iconCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)

        label1 = tk.Label(iconCanvas, image=self.imagePhoto, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        label1.pack()

    def initMiddleLeft(self, master):
        hour = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.time['hour'], font=("Times", 35,"bold") )
        hour.pack(anchor=tk.N, fill=tk.X, expand=1)

        date = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.time['date'], font=("Helvetica", 12,"bold"))
        date.pack(anchor=tk.S)

    def turn_on_video_output(self, event):
        subprocess.call(["vcgencmd", "display_power", "1"], stdout=subprocess.DEVNULL)

    def exit(self, event):
        self.quit()