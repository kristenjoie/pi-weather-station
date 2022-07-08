#!/usr/bin/env python

##
# UI
# #

import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import os

BACKGROUND_COLOR = "#101012"
FOREGROUND_COLOR = "#adadad"

class WeatherUI(tk.Tk) :
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen",True)
        self.title("Pi Weather Station")
        self.bind("<Double-Button-1>", self.exit)
        self.bind("<Button-1>", self.turn_on_video_output) # to turn off video_output, we use cron table 

        self.room = {
            "name": tk.StringVar(self, "Room"),
            "temperature": tk.StringVar(self, "---- °C"),
            "humidity": tk.StringVar(self, "---- %"),
            "pressure": tk.StringVar(self, "----"),
            "air_quality": tk.StringVar(self, "Air: :-)")
        }
        self.outside = {
            "name": tk.StringVar(self, "Outside"),
            "temperature": tk.StringVar(self, "---- °C "),
            "humidity": tk.StringVar(self, "---- %"),
            "wind": tk.StringVar(self, "---- N"),
            "air_quality": tk.StringVar(self, "Air: :-)"),
            "condition": tk.StringVar(self, "----"),
            "sun_time": tk.StringVar(self, "sunTime: 00:00:00")
        }

        self.time = {
            "hour": tk.StringVar(self, "00:00:00"),
            "date": tk.StringVar(self, "1 Jan"),
        }

        ##
        # The GUI use those canvas:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 
        #                               backgroundCanvas
        # 
        # - - - - - - - - - - - - - - - sensorFooterCanvas- - - - - - - - - - - -
        # roomCanvas           timeCanvas      conditionCanvas        outsideCanvas
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # #
        #---------------------------------------------------------------
        self.imageBackground = Image.open(os.path.dirname(os.path.realpath(__file__)) + '/icons/background.jpg')
        self.imageIcon = Image.open(os.path.dirname(os.path.realpath(__file__))+"/icons/10d@2x.png")

        self.initBackground()
        self.initFooterCanvas()
        self.initForecastFooterCanvas()
        
    def initBackground(self):
        
        backgroundCanvas = tk.Canvas(self,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        backgroundCanvas.pack(fill=tk.BOTH, expand=1)
        backgroundCanvas.update()

        img_w, img_h = self.imageBackground.size
        width_factor = backgroundCanvas.winfo_width() / img_w
        height_factor = backgroundCanvas.winfo_height() / img_h
        factor = min(width_factor, height_factor)
        self.imageBackground = self.imageBackground.resize((int(img_w*factor) , int(img_h*factor)))
        self.imagePhotoBackground = ImageTk.PhotoImage(self.imageBackground)
        
        imageBackgroundLabel = tk.Label(backgroundCanvas, image=self.imagePhotoBackground, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        imageBackgroundLabel.pack()


    def initFooterCanvas(self):
        self.sensorFooterCanvas = tk.Canvas(self,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.sensorFooterCanvas.pack(anchor=tk.S, fill=tk.X)

        roomCanvas = tk.Canvas(self.sensorFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        roomCanvas.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.initRoomWidget(roomCanvas)
        
        outsideCanvas = tk.Canvas(self.sensorFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        outsideCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.initOutsideWidget(outsideCanvas)
        
        timeCanvas = tk.Canvas(self.sensorFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        timeCanvas.pack(side=tk.LEFT, fill=tk.X, expand=1)
        self.initTimeWidget(timeCanvas)

        conditionCanvas = tk.Canvas(self.sensorFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        conditionCanvas.pack(side=tk.RIGHT, fill=tk.X, expand=1)
        self.initConditionWidget(conditionCanvas)

    def showSensorFooter(self):
        self.sensorFooterCanvas.pack(anchor=tk.S, fill=tk.BOTH)

    def hideSensorFooter(self):
        self.sensorFooterCanvas.pack_forget()

        ##
        # The GUI use those canvas:
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # 
        #                               backgroundCanvas
        # 
        # - - - - - - - - - - - - - - - initForecastFooterCanvas- - - - - - - - - 
        # forecastFooterCanvas                      | dayOneCanvas | dayTwoCanvas
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        # #
        #---------------------------------------------------------------
    def initForecastFooterCanvas(self):
        self.forecastFooterCanvas = tk.Frame(self,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.currentDayCanvas = tk.Frame(self.forecastFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.currentDayCanvas.pack(anchor=tk.S, side=tk.LEFT, fill=tk.X)
        self.initCurrentForecast()
        
        self.dayTwoCanvas = tk.Frame(self.forecastFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.dayTwoCanvas.pack(side=tk.RIGHT)
        dayTwolabel = tk.Label(self.dayTwoCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, text="D+2", font=("Helvetica", 10,"bold"))
        dayTwolabel.pack(anchor=tk.NW)
        septwo = tk.Label(self.forecastFooterCanvas, fg=FOREGROUND_COLOR, bg=FOREGROUND_COLOR, text="|", font=("Helvetica",5,"bold"))
        septwo.pack(side=tk.RIGHT, fill=tk.Y)
        self.initDayTwoForecast()

        self.dayOneCanvas = tk.Frame(self.forecastFooterCanvas,  bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.dayOneCanvas.pack(side=tk.RIGHT)
        dayOnelabel = tk.Label(self.dayOneCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, text="D+1", font=("Helvetica", 10,"bold"))
        dayOnelabel.pack(anchor=tk.NW)
        sep = tk.Label(self.forecastFooterCanvas, fg=FOREGROUND_COLOR, bg=FOREGROUND_COLOR, text="|", font=("Helvetica", 5,"bold"))
        sep.pack(side=tk.RIGHT, fill=tk.Y)
        self.initDayOneForecast()

    def initCurrentForecast(self):
        one = ForecastWidget(self.currentDayCanvas, tk.LEFT, "09H")
        two = ForecastWidget(self.currentDayCanvas, tk.LEFT, "12H")
        three = ForecastWidget(self.currentDayCanvas, tk.LEFT, "15H")
        four = ForecastWidget(self.currentDayCanvas, tk.LEFT, "18H")
        five = ForecastWidget(self.currentDayCanvas, tk.LEFT, "21H")
        self.currentForecast = [one, two, three, four, five]

    def initDayOneForecast(self):
        self.dayonenine = ForecastWidget(self.dayOneCanvas, tk.LEFT, "09H")
        self.dayonefifteen = ForecastWidget(self.dayOneCanvas, tk.LEFT, "15H")
        self.dayonetwentyone = ForecastWidget(self.dayOneCanvas, tk.LEFT, "21H")
    
    def initDayTwoForecast(self):
        self.daytwonine = ForecastWidget(self.dayTwoCanvas, tk.LEFT, "09H")
        self.daytwofifteen = ForecastWidget(self.dayTwoCanvas, tk.LEFT, "15H")
        self.daytwotwentyone = ForecastWidget(self.dayTwoCanvas, tk.LEFT, "21H")

    def showForecastFooter(self):
        self.forecastFooterCanvas.pack(anchor=tk.S, fill=tk.BOTH)

    def hideForecastFooter(self):
        self.forecastFooterCanvas.pack_forget()
    
    def initRoomWidget(self, master) :
        nameLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["name"], font=("Helvetica", 15,"bold"))
        nameLabel.pack(anchor=tk.NW)

        temperatureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["temperature"], font=("Helvetica", 30,"bold"))
        temperatureLabel.pack(side=tk.LEFT)

        humidityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["humidity"], font=("Helvetica", 12,"bold"))
        humidityLabel.pack(anchor=tk.SW)
        pressureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["pressure"], font=("Helvetica", 12,"bold"))
        pressureLabel.pack(anchor=tk.SW)
        airQualityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.room["air_quality"], font=("Helvetica", 12,"bold"))
        airQualityLabel.pack(anchor=tk.SW)

    def initOutsideWidget(self, master) :
        nameLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["name"], font=("Helvetica", 15,"bold"))
        nameLabel.pack(anchor=tk.NE)

        temperatureLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["temperature"], font=("Helvetica", 30,"bold"))
        temperatureLabel.pack(side=tk.RIGHT)

        humidityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["humidity"], font=("Helvetica", 12,"bold"))
        humidityLabel.pack(anchor=tk.SE)
        windLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["wind"], font=("Helvetica", 12,"bold"))
        windLabel.pack(anchor=tk.SE)
        airQualityLabel = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["air_quality"], font=("Helvetica", 12,"bold"))
        airQualityLabel.pack(anchor=tk.SE)

    def initConditionWidget(self, master) :
        detailCanvas = tk.Canvas(master, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        detailCanvas.pack(side=tk.RIGHT)

        conditionLabel = tk.Label(detailCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["condition"], font=("Helvetica", 25,"bold"))
        conditionLabel.pack()

        sunTimeLabel = tk.Label(detailCanvas, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.outside["sun_time"], font=("Helvetica", 15,"bold"))
        sunTimeLabel.pack()
        
        self.imageIcon = self.imageIcon.resize((100,100))
        self.imagePhoto = ImageTk.PhotoImage(self.imageIcon)

        iconCanvas = tk.Canvas(master, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        iconCanvas.pack(side=tk.RIGHT)

        self.imageIconLabel = tk.Label(iconCanvas, image=self.imagePhoto, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.imageIconLabel.pack()

    def initTimeWidget(self, master):
        hour = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.time['hour'], font=("Times", 35,"bold") )
        hour.pack(anchor=tk.N, fill=tk.X, expand=1)

        date = tk.Label(master, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.time['date'], font=("Helvetica", 12,"bold"))
        date.pack(anchor=tk.S)

    def update_icon_image(self, path):
        self.imageIcon = Image.open(path).resize((100,100))
        self.imagePhoto = ImageTk.PhotoImage(self.imageIcon)
        self.imageIconLabel.configure(image=self.imagePhoto)


    def turn_on_video_output(self, event):
        subprocess.call(["vcgencmd", "display_power", "1"], stdout=subprocess.DEVNULL)

    def exit(self, event):
        self.quit()

class ForecastWidget():
    def __init__(self, master, side, label) -> None:
        self.title = tk.StringVar(master, label)
        self.temp = tk.StringVar(master, "15 °C")
        self.rain = tk.StringVar(master, "0 mm")

        widg = tk.Canvas(master, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        widg.pack(side=side)

        label = tk.Label(widg, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.title, font=("Helvetica", 10))
        label.pack(side=tk.TOP)

        iconCanvas = tk.Canvas(widg, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        iconCanvas.pack(side=tk.LEFT)

        self.imageIconLabel = tk.Label(iconCanvas, bg=BACKGROUND_COLOR, borderwidth = 0, highlightthickness = 0)
        self.imageIconLabel.pack()

        temp = tk.Label(widg, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.temp, font=("Helvetica", 8,"bold"))
        temp.pack()
        rain = tk.Label(widg, fg=FOREGROUND_COLOR, bg=BACKGROUND_COLOR, textvariable=self.rain, font=("Helvetica", 8,"bold"))
        rain.pack()
        
    def setIcon(self, img):
        self.imageIconLabel.configure(image=img)
    
    def buildForecastImageObject(self, path):
        img = Image.open(path)
        img = img.resize((50,50))
        img = ImageTk.PhotoImage(img)
        return img
