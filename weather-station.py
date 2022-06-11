#!/usr/bin/env python

##
# GUI to display data from the server station
# #

import requests
import locale
import os
import time
import threading
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("api_key", type=str, help="OpenWeather Map API key")
parser.add_argument("-l", "--locale", type=str, default="en_GB", help="Choose locale")
parser.add_argument("--lat", type=str, help="location latitude")
parser.add_argument("--lon", type=str, help="location longitude")
parser.add_argument("--city", type=str, help="location city name. Format is {city name},{state code},{country code}")
args = parser.parse_args()

##
#  load config file
# #
SENSOR_LIST = json.loads(open("sensor.config.json").read())

##
# LOCALES
# #
LOCALE = args.locale
LANGUAGE = args.locale[:2]
locale.setlocale(locale.LC_TIME, LOCALE)
# load translation file
TXT = json.loads(open("locales/{}.json".format(LOCALE)).read())

##
# Refresh time
# # 
SENSOR_REFRESH_TIME = 10 # 10 seconds
API_REFRESH_TIME = 300 # 5 minutes

##
# API OPENWEATHER
# #
API_KEY = args.api_key
API_LAT = args.lat
API_LON = args.lon
API_CITY = args.city

def get_api_location():
    url = "http://api.openweathermap.org/geo/1.0/direct?q={}&appid={}".format(API_CITY, API_KEY)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 30, verify = False )
    return r.json()[0]["lat"], r.json()[0]["lon"]

def get_api_current_weather():
    url = "http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&units=metric&lang={}&appid={}".format(API_LAT, API_LON, LANGUAGE, API_KEY)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 30, verify = False )
    return r.json()

def get_api_pollution():
    url = "http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}".format(API_LAT, API_LON, API_KEY)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 30, verify = False )
    return r.json()

def download_api_icon(name, path):
    r = requests.get('http://openweathermap.org/img/wn/{}@2x.png'.format(name))
    open(path, 'wb').write(r.content)

def get_sensor_data(ip, port):
    url = "http://{}:{}".format(ip, port)
    r = requests.get(url, headers={'Cache-Control': 'no-cache'}, timeout = 10)
    return r.json()
    # to debug
    # return json.loads('{"type":"bmp", "temperature":20, "humidity":68.9, "pressure":1201, "air_quality_text":"GOOD"}')

##
# Update Display
# #
def update_room_data(window):
    while True:
        for room in SENSOR_LIST :
            room_data = get_sensor_data(room["ip"], room["port"])
            window.room["name"].set("{}".format(room["name"]))
            # if sensor does not send temperature, we do not update the display, so there may be some inconsistencies
            if "temperature" in room_data: window.room["temperature"].set("{} °C".format(room_data["temperature"]))
            if "humidity" in room_data: window.room["humidity"].set("{} %".format(room_data["humidity"]))
            if "pressure" in room_data: window.room["pressure"].set("{}".format(room_data["pressure"]))
            if "air_quality_text" in room_data: window.room["air_quality"].set("{}".format(room_data["air_quality_text"].capitalize()))
            time.sleep(SENSOR_REFRESH_TIME)

def update_hour(window):
    window.time["hour"].set(time.strftime("%H:%M:%S", time.localtime()))
    window.time["date"].set(time.strftime("%A %-d %b", time.localtime()).title())
    window.after(1000, update_hour, window)

def update_api_data(window):
    global API_LAT, API_LON
    if API_LAT is None:
        if API_CITY is None:
            raise ValueError("You must set latitude, longitude or city name")
        else:
            API_LAT, API_LON = get_api_location()
            print("We found lat:{} and lon:{} for city:{}".format(API_LAT, API_LON, API_CITY))

    while True:
        weather_data = get_api_current_weather()
        pollution_data = get_api_pollution()
        window.outside["name"].set("{}".format(weather_data["name"]))
        window.outside["temperature"].set("{} °C".format("%.1f" % weather_data["main"]["temp"]))
        window.outside["humidity"].set("{} %".format("%.1f" % weather_data["main"]["humidity"]))
        
        wind_speed, wind_direction = format_wind_info(weather_data)
        window.outside["wind"].set("{} km/h {}".format(wind_speed, wind_direction))
        window.outside["air_quality"].set("{}".format(format_air_quality(pollution_data).capitalize()))
        window.outside["condition"].set("{}".format(weather_data['weather'][0]['description'].title()))
        window.outside["sun_time"].set("{}".format(format_sun_time(weather_data)))

        set_weather_icon(window, weather_data['weather'][0]['icon'])
        time.sleep(API_REFRESH_TIME)

def set_weather_icon(window, icon_name):
    path = 'icons/{}@2x.png'.format(icon_name)
    if not os.path.exists(path):
        download_api_icon(icon_name, path)
    window.update_icon_image(path)

def format_sun_time(weather):
    sunrise = weather["sys"]["sunrise"]
    sunset = weather["sys"]["sunset"]
    current = time.time()
    if current < sunrise :
        return "{} {}".format(TXT["SUNRISE"] ,time.strftime("%H:%M", time.localtime(sunrise)))
    elif current < sunset :
        return "{} {}".format(TXT["SUNSET"] ,time.strftime("%H:%M", time.localtime(sunset)))
    else :
        return ""

def format_wind_info(weather):
    if 'wind' in weather:
        wind_speed = "%.1f" % (int(weather['wind']['speed']) *3.6)
        if 'deg' in weather['wind']:
            wind_direction = int(weather['wind']['deg'])
        else :
            wind_direction = 0
    else: 
        wind_speed = 0
        wind_direction = 0
    val=int((wind_direction/22.5)+.5)
    arr=[TXT['NORTH'],"{}{}{}".format(TXT['NORTH'],TXT['NORTH'],TXT['EAST']),"{}{}".format(TXT['NORTH'],TXT['EAST']),"{}{}{}".format(TXT['EAST'],TXT['NORTH'],TXT['EAST']),
    TXT['EAST'],"{}{}{}".format(TXT['EAST'],TXT['SOUTH'],TXT['EAST']),"{}{}".format(TXT['SOUTH'],TXT['EAST']), "{}{}{}".format(TXT['SOUTH'],TXT['SOUTH'],TXT['EAST']),
    TXT['SOUTH'],"{}{}{}".format(TXT['SOUTH'],TXT['SOUTH'],TXT['WEST']),"{}{}".format(TXT['SOUTH'],TXT['WEST']),"{}{}{}".format(TXT['WEST'],TXT['SOUTH'],TXT['WEST']),
    TXT['WEST'],"{}{}{}".format(TXT['WEST'],TXT['NORTH'],TXT['WEST']),"{}{}".format(TXT['NORTH'],TXT['WEST']),"{}{}{}".format(TXT['NORTH'],TXT['NORTH'],TXT['WEST'])]
    wind_direction = arr[(val % 16)]
    return wind_speed, wind_direction

def format_air_quality(pollution):
    if   pollution["list"][0]["main"]["aqi"] == 5: return TXT["VERY_POOR"]
    elif pollution["list"][0]["main"]["aqi"] == 4: return TXT["POOR"]
    elif pollution["list"][0]["main"]["aqi"] == 3: return TXT["MEDIOCRE"]
    elif pollution["list"][0]["main"]["aqi"] == 2: return TXT["MODERATE"]
    elif pollution["list"][0]["main"]["aqi"] == 1 : return TXT["GOOD"]

##
# TKinter Canvas
# #
from weatherUI import WeatherUI

if __name__ == '__main__':
    window = WeatherUI()
    window.after(1000, update_hour, window)

    # update Sensors Info
    sensor_t = threading.Thread(target=update_room_data, args=(window, ), daemon=True)
    sensor_t.start()

    # update API info
    api_t = threading.Thread(target=update_api_data, args=(window, ), daemon=True)
    api_t.start()

    window.mainloop()