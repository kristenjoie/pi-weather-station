#!/usr/bin/env python

##
# GUI to display data from the server station
# #

import requests
import locale
import os
import time
import datetime
import threading
import json
import argparse
import pandas

parser = argparse.ArgumentParser()
parser.add_argument("api_key", type=str, help="OpenWeather Map API key")
parser.add_argument("-l", "--locale", type=str, default="en_GB", help="Choose locale")
parser.add_argument("--lat", type=str, help="location latitude")
parser.add_argument("--lon", type=str, help="location longitude")
parser.add_argument("--city", type=str, help="location city name. Format is {city name},{state code},{country code}")
parser.add_argument("--influxdb", action='store_true', help="Use InfluxDB")
parser.add_argument("--influxdb_host", type=str, help="InfluxDB host")
parser.add_argument("--influxdb_port", type=int, help="InfluxDB port")
parser.add_argument("--influxdb_database", type=str, help="InfluxDB database")

args = parser.parse_args()

##
#  load config file
# #
SENSOR_LIST = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/sensor.config.json").read())

##
# LOCALES
# #
LOCALE = args.locale
locale.setlocale(locale.LC_TIME, LOCALE)
LOCALE = LOCALE.split(".")[0]
LANGUAGE = LOCALE[:2]
# load translation file
TXT = json.loads(open("{}/locales/{}.json".format(os.path.dirname(os.path.realpath(__file__)), LOCALE)).read())

##
# Refresh time
# # 
SENSOR_REFRESH_TIME = 5 # 5 seconds
API_REFRESH_TIME = 300 # 5 minutes
API_FORECAST_REFRESH_TIME = 10800 # 3 hours

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

def get_api_forecast_weather():
    url = "http://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&units=metric&lang={}&appid={}".format(API_LAT, API_LON, LANGUAGE, API_KEY)
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
    # return json.loads('{"type":"bmp", "temperature":20, "humidity":68.9, "pressure":1201, "score": 50, "air_quality_text":"GOOD"}')

##
# Update Display
# #
def update_room_data(window):
    while True:
        for room in SENSOR_LIST :
            try:
                room_data = get_sensor_data(room["ip"], room["port"])
                window.room["name"].set("{}".format(room["name"].capitalize()))
                # if sensor does not send temperature, we do not update the display, so there may be some inconsistencies
                temperature, humidity, pressure, air_quality_score= None, None, None, None
                if "temperature" in room_data: 
                    temperature = room_data["temperature"]
                    window.room["temperature"].set("{} °C".format(temperature))
                if "humidity" in room_data: 
                    humidity = room_data["humidity"]
                    window.room["humidity"].set("{} %".format(humidity))
                if "pressure" in room_data: 
                    pressure = room_data["pressure"]
                    window.room["pressure"].set("{} mb".format(pressure))
                if "air_quality_text" in room_data:
                    window.room["air_quality"].set("{}".format(room_data["air_quality_text"].capitalize()))
                if "score" in room_data:
                    air_quality_score = room_data["score"]

                if args.influxdb:
                    populate_influxdb("temp", room["influxdb_source_name"], type=room_data["type"], temperature=temperature, humidity=humidity, pressure=pressure, air_quality_score=air_quality_score)
            except :
                pass
            time.sleep(SENSOR_REFRESH_TIME)
        switchBetweenCurrentAndForecast(window, SENSOR_REFRESH_TIME*2)

def switchBetweenCurrentAndForecast(window, wait_time):
    window.hideSensorFooter()
    window.showForecastFooter()
    time.sleep(wait_time)
    window.hideForecastFooter()
    window.showSensorFooter()

def update_hour(window):
    window.time["hour"].set(time.strftime("%H:%M:%S", time.localtime()))
    window.time["date"].set(time.strftime("%A %-d %B", time.localtime()).title())
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
        try :
            weather_data = get_api_current_weather()
            pollution_data = get_api_pollution()
            window.outside["name"].set("{}".format(weather_data["name"].capitalize()))
            window.outside["temperature"].set("{} °C".format("%.1f" % weather_data["main"]["temp"]))
            window.outside["humidity"].set("{} %".format("%.1f" % weather_data["main"]["humidity"]))
            
            wind_speed, wind_direction = format_wind_info(weather_data)
            window.outside["wind"].set("{} km/h {}".format(wind_speed, wind_direction))
            window.outside["air_quality"].set("{}".format(format_air_quality(pollution_data).capitalize()))
            window.outside["condition"].set("{}".format(weather_data['weather'][0]['description'].title()))
            window.outside["sun_time"].set("{}".format(format_sun_time(weather_data)))

            set_weather_icon(window, weather_data['weather'][0]['icon'])
            
            clouds = 0 if 'clouds' not in weather_data else weather_data["clouds"]["all"]
            if args.influxdb:
                populate_influxdb("temp", "web",temperature=weather_data["main"]["temp"],
                    humidity= weather_data["main"]["humidity"], wind_speed=wind_speed, wind_direction=weather_data['wind']['deg'], clouds=clouds)
        except:
            pass
        time.sleep(API_REFRESH_TIME)

def update_api_forecast(window):
    global API_LAT, API_LON
    if API_LAT is None:
        if API_CITY is None:
            raise ValueError("You must set latitude, longitude or city name")
        else:
            API_LAT, API_LON = get_api_location()
            print("We found lat:{} and lon:{} for city:{}".format(API_LAT, API_LON, API_CITY))

    img =  [None] * len(window.currentForecast)
    while True:
        try:
            forecast_data = get_api_forecast_weather()
            df = pandas.DataFrame(forecast_data["list"]) 
            # for the current day
            for index, item in enumerate(window.currentForecast):
                item.title.set("{}H".format(time.strftime("%H", time.gmtime(df["dt"][1+index]))))
                img[index] = set_forecast_value(item, df.iloc[1+index])

            # for D+1
            forecast_img = [None] * 6
            df.set_index('dt', inplace=True)
            forecast_img[0] = set_forecast_value(window.dayonenine, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 09:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
            forecast_img[1] = set_forecast_value(window.dayonefifteen, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 15:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
            forecast_img[2] = set_forecast_value(window.dayonetwentyone, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d 21:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
            
            # for D+2
            forecast_img[3] = set_forecast_value(window.daytwonine, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d 09:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
            forecast_img[4] = set_forecast_value(window.daytwofifteen, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d 15:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
            forecast_img[5] = set_forecast_value(window.daytwotwentyone, df.loc[datetime.datetime.strptime((datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d 21:00:00"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc).timestamp()])
        except:
            pass
        time.sleep(API_FORECAST_REFRESH_TIME)

def set_forecast_value(item, dataframe):
    item.temp.set("{} °C".format("%.1f" % dataframe["main"]["temp"]))
    if "rain" in dataframe and pandas.notnull(dataframe["rain"]) and "3h" in dataframe["rain"]:
        item.rain.set("{} mm".format("%.1f" % dataframe["rain"]["3h"]))
    else:
        item.rain.set("0 mm")
    path = download_icon(dataframe["weather"][0]["icon"])
    img = item.buildForecastImageObject(path)
    item.setIcon(img)
    return img

def set_weather_icon(window, icon_name):
    path = download_icon(icon_name)
    window.update_icon_image(path)

def download_icon(icon_name):
    path = '{}/icons/{}@2x.png'.format(os.path.dirname(os.path.realpath(__file__)), icon_name)
    if not os.path.exists(path):
        download_api_icon(icon_name, path)
    return path

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
    if len(pollution["list"]) > 0 :
        if   pollution["list"][0]["main"]["aqi"] == 5: return TXT["VERY_POOR"]
        elif pollution["list"][0]["main"]["aqi"] == 4: return TXT["POOR"]
        elif pollution["list"][0]["main"]["aqi"] == 3: return TXT["MEDIOCRE"]
        elif pollution["list"][0]["main"]["aqi"] == 2: return TXT["MODERATE"]
        elif pollution["list"][0]["main"]["aqi"] == 1 : return TXT["GOOD"]
    else:
        return TXT["UNKNOWN"]
##
# Influxdb
# #
if args.influxdb:
    from influxdb import InfluxDBClient
    client = InfluxDBClient(host=args.influxdb_host, port=args.influxdb_port, database=args.influxdb_database, timeout=30)

def populate_influxdb(measurement, source, temperature, type=None, humidity = None, pressure = None, air_quality_score = None, wind_speed = None, wind_direction = None, clouds = None):
    json_body = [
        { 
            "measurement": measurement,
            "tags": {
                "source": source
            },
            "time": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "fields": {
                "temperature": temperature,
            }
        }
    ]
    if type is not None :
        json_body[0]["tags"]["type"] = type
    list_item = {"humidity":humidity, "pressure":pressure, "air_quality_score":air_quality_score, "wind_speed":wind_speed, "wind_direction":wind_direction, "clouds":clouds}
    for item in list_item:
        if list_item[item] is not None: 
            json_body[0]["fields"][item] = float(list_item[item])
            if item == "clouds"or item == "wind_direction":
                 json_body[0]["fields"][item] = int(json_body[0]["fields"][item])
    client.write_points(json_body)

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

    # update API Forecast Info
    api_forecast_t = threading.Thread(target=update_api_forecast, args=(window, ), daemon=True)
    api_forecast_t.start()

    window.mainloop()