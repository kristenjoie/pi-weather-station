#!/usr/bin/env python

##
# GUI to display data from the server station
# #

import requests
import locale
import os

API_OPENWEATHERMAP_KEY = os.environ.get('API_OPENWEATHERMAP_KEY')
API_OPENWEATHERMAP_LOCATION = os.environ.get('API_OPENWEATHERMAP_LOCATION')

locale.setlocale(locale.LC_TIME, "fr_FR")

def get_api_openweather_data(location, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&lang=fr&appid={}".format(location, api_key)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 60, verify = False )
    return r.json()

def get_sensor_data(ip, port):
    url = "http://{}:{}".format(ip, port)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'})
    return r.json()


##
# TKinter Canvas
# #
from weatherUI import WeatherUI

if __name__ == '__main__':
    window = WeatherUI()
    window.mainloop()