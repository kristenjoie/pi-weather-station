# pi-weather-station

A Weather Station for the Raspberry Pi with bme680 and bmp280 sensors. 
Written in Python with TKinter and Flask.  
To get more weather data, we use [OpenWeather](https://openweathermap.org)

![screenshot](screenshot.png)

## 🚥 Pre-requisites

- Make sure that I2c is configured on the Raspberry Pi.
Please follow this tutorial -> https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

- You are registered and have an api key from [openweathermap.org](https://openweathermap.org)

## 🏗️ Install

The easiest way is:
```
pip3 install -r requirements.txt
``` 

<details close>
<summary>In details:</summary>
<br>

 - For server
https://learn.adafruit.com/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout/overview
```
sudo pip3 install adafruit-circuitpython-bmp280
sudo pip3 install board
```
&&  
https://learn.pimoroni.com/article/getting-started-with-bme680-breakout
```
sudo pip3 install bme680
```

 - For the display
```
sudo pip3 install pillow
```

 - For influxdb
```
sudo pip3 install influxdb
```
</details>
  

## ⚙️ Configuration

For sensors configuration, edit file [sensor.config.json](sensor.config.json). You can add many sensor you want. Data displayed will rotate every 10 seconds.

## 🚀 Run
### Sensor Server:
On each Raspberry Pi, run command
```
python3 sensor-server.py <sensor_type> <server_port>[--temperature_offset <int>] &
```
With: 
- `sensor_type` can be : "bme" or "bmp"
- `server_port` the server port, default value is 80.
- `temperature_offset` is optional, you need to a second thermometer to adjust the offset value if needed (Note: for bme680 sensor, to get accurate gas measurements, we need to  "burn in" the sensor during 20 minutes)

### Display:
Run command:
```
python3 weather-station.py <api-key> --lat <lat> --lon <lon>
```
With:
- `api-key`, your openWeather Map API key.
- `lat` and `lon`, latitude and longitude for your location.  
There are optionals arguments:
- `--city`: If you don't know the location latitude and longitude, you can use the city name. The format is `{city name},{state code},{country code}`. More details [here](https://openweathermap.org/api/geocoding-api#direct).  
It's preferable to use latitude and longitude.
- `--locale`: to change the locale. If you need can add translation file in folder [./locales](./locales/)

### InfluxDB:
To store data and use it in an external tools, we use [InfluxDB](https://www.influxdata.com/).  

Add arguments to the run command:
```
 --influxdb --influxdb_host localhost --influxdb_port 8086 --influxdb_database weather
```

## 📖 More info
Sensor data will be updated every 10s
API data will be fetched every 5 minutes.

For the display, we use a GeekPi 7 inch. To avoid keeping the screen on all day, we use a cron table with the command `vcgencmd display_power 0` to turn it off.
To turn on the screen, you just need to tap the screen.
To quit the app, you just need double-tap the screen.
