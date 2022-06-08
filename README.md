# pi-weather-station

A Weather Station for the Raspberry Pi with bme680 and bmp280 sensors. 
Written in Python with TKinter and Flask.

## 🚥 Pre-requisites

Make sure that I2c is configured on the Raspberry Pi.
Please follow this tutorial -> https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c

## 🏗️ Install

The easiest way is:
```
pip3 install -r requirements.txt
``` 

In details:
for server
https://learn.adafruit.com/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout/overview
```
sudo pip3 install adafruit-circuitpython-bmp280
```
&&  
https://learn.pimoroni.com/article/getting-started-with-bme680-breakout
```
sudo pip3 install bme680
```

For the display
```
sudo pip3 install pillow
```

For influxdb
```
sudo pip3 install influxdb
```

## 🚀 Run
To run the server part
```
python3 sensor-server.py <sensor_type> [--temperature_offset <int>] &
```
- sensor_type can be : "bme" or "bmp"
- temperature_offset is optional, you need to an second thermometer to adjust the offset value if needed 
