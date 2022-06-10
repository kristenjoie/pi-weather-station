#!/usr/bin/env python

##
# GUI to display data from the server station
# #

import requests
import locale
import os
import time
import threading
import traceback
import json

SENSOR_LIST = json.loads(open("sensor.config.json").read())

API_OPENWEATHERMAP_KEY = os.environ.get('API_OPENWEATHERMAP_KEY')
API_OPENWEATHERMAP_LOCATION = os.environ.get('API_OPENWEATHERMAP_LOCATION')

locale.setlocale(locale.LC_TIME, "fr_FR")

STOP_FLAG = False

SENSOR_REFRESH_TIME = 10 # 10 seconds

# TODO: find lat @ lon
# http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}

# TODO: air quality
# https://api.openweathermap.org/data/2.5/air_pollution?lat=<lat>&lon=<lon>&appid=<apikey>

def get_api_openweather_data(location, api_key):
    # TODO: change request to replace cityid by lat & lon
    url = "http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&lang=fr&appid={}".format(location, api_key)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 30, verify = False )
    return r.json()

def get_sensor_data(ip, port):
    url = "http://{}:{}".format(ip, port)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 10)
    return r.json()
    # to debug
    # return json.loads('{"type":"bmp", "temperature":20, "humidity":68.9, "pressure":1201, "air_quality_text":"ok"}')

def inside_room_data(window):
    while True and not STOP_FLAG:
        try: 
            for room in SENSOR_LIST :
                room_data = get_sensor_data(room["ip"], room["port"])
                window.room["name"].set("{}".format(room["name"]))
                # if sensor does not send temperature, we do not update the display, so there may be some inconsistencies
                if "temperature" in room_data: window.room["temperature"].set("{} °C".format(room_data["temperature"]))
                if "humidity" in room_data: window.room["humidity"].set("{} %".format(room_data["humidity"]))
                if "pressure" in room_data: window.room["pressure"].set("{}".format(room_data["pressure"]))
                if "air_quality_text" in room_data: window.room["air_quality"].set("Inside Air: {}".format(room_data["air_quality_text"]))
                time.sleep(SENSOR_REFRESH_TIME)
        except Exception as e :
            if not STOP_FLAG:
                traceback.print_exc()
            break

def update_hour(window):
    window.time["hour"].set(time.strftime("%H:%M:%S", time.localtime()))
    window.time["date"].set(time.strftime("%A %-d %b", time.localtime()).title())
    window.after(1000, update_hour, window)


##
# TKinter Canvas
# #
from weatherUI import WeatherUI

if __name__ == '__main__':
    window = WeatherUI()
    window.after(1000, update_hour, window)

    # update Sensors Info
    sensor_t = threading.Thread(target=inside_room_data, args=(window, ))
    sensor_t.start()


    window.mainloop()
    # only app is stopped
    STOP_FLAG = True # stopping Threads