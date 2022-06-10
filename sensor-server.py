#!/usr/bin/env python

##
# Script to get data from sensor
# Create a Flask to diffuse those data
# #

import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("sensor_type", type=str,
                    help="display a square of a given number")
parser.add_argument("-t", "--temperature_offset", type=int, default=0,
                    help="Add an Offset to temperature")
args = parser.parse_args()

if args.sensor_type == 'bmp':
    import adafruit_bmp280
    import board
    import busio

    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

elif args.sensor_type == 'bme':
    import bme680
    import threading

    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
    
    global gas, gas_baseline, hum, air_quality_score

    gas = 250000
    gas_baseline = 250000
    hum = 40
    air_quality_score = 100

    def sensor_background():
        global gas, gas_baseline, hum, air_quality_score

        start_time = time.time()
        curr_time = time.time()
        burn_in_time = 1200
        print('Collecting gas resistance burn-in data for 20 mins\n')

        # start burn-in processs
        burn_in_data = []
        while curr_time - start_time < burn_in_time:
            curr_time = time.time()
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                gas = sensor.data.gas_resistance
                burn_in_data.append(gas)
                print('Gas: {0} Ohms'.format(gas))

                time.sleep(1)
        # end burn-in 
        gas_baseline = sum(burn_in_data[-50:]) / 50.0
        hum_baseline = 40.0
        hum_weighting = 0.25
        while True:
            if sensor.get_sensor_data() and sensor.data.heat_stable:
                gas = sensor.data.gas_resistance
                gas_offset = gas_baseline - gas

                hum = sensor.data.humidity
                hum_offset = hum - hum_baseline

                # Calculate hum_score as the distance from the hum_baseline.
                if hum_offset > 0:
                    hum_score = (100 - hum_baseline - hum_offset)
                    hum_score /= (100 - hum_baseline)
                    hum_score *= (hum_weighting * 100)

                else:
                    hum_score = (hum_baseline + hum_offset)
                    hum_score /= hum_baseline
                    hum_score *= (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline)
                    gas_score *= (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score.
                air_quality_score = hum_score + gas_score
                time.sleep(5)

    def get_air_quality():
        score = (100-air_quality_score)*5
        # air_quality = score
        if   (score >= 301) : IAQ_text = "Dangereux"
        elif (score >= 201 and score <= 300 ): IAQ_text = "Mauvais"
        elif (score >= 176 and score <= 200 ): IAQ_text = "Médiocre"
        elif (score >= 151 and score <= 175 ): IAQ_text = "Modéré"
        elif (score >=  51 and score <= 150 ): IAQ_text = "Bon"
        elif (score >=  00 and score <=  50 ): IAQ_text = "Très Bon"
        return gas, air_quality_score, score, IAQ_text

    t = threading.Thread(name='sensor_background', target=sensor_background)
    t.start()

else :
    print("Unknown sensor type, can be 'bmp' or 'bme'")
    exit(-1)


##
# Flask App
# #
from flask import Flask
from flask import jsonify

app = Flask(__name__)


@app.route('/') # return data info in json format
def temp():
    if ( args.sensor_type == 'bmp'):
        return jsonify(type="bmp",
                   temperature=float("%.1f" % sensor.temperature + args.temperature_offset),
                   pressure=float("%.1f" % sensor.pressure))
    elif (args.sensor_type == 'bme'):
        gas, air_quality, score, air_quality_text = get_air_quality()
        return jsonify(type="bme",
                   temperature=float("%.1f" % sensor.data.temperature + args.temperature_offset),
                   humidity=float("%.1f" % sensor.data.humidity),
                   gas_ref= float("%.1f" % gas_baseline),
                   gas_sensor=float("%.1f" % gas),
                   air_quality=float("%.1f" % air_quality),
                   score=float("%.1f" % score),
                   air_quality_text=air_quality_text,
                   pressure=float("%.1f" % sensor.data.pressure))

@app.route('/set/<int:gas>') # if need to adjust 'gas_baseline' after burn-in time 
def set(gas):
    global gas_baseline
    gas_baseline = gas
    return "Value setted"

@app.route('/home') # just dislpay temperature in full screen
def home():
    if (args.sensor_type == 'bmp'):
        temperature= "%.1f" % sensor.temperature + args.temperature_offset
    elif (args.sensor_type == 'bme'):
        temperature = "%.1f" % sensor.data.temperature + args.temperature_offset
    
    return """
    <style>
    body {background-color: black;}
    h1 {color: white;
        height:100%;
        width:100%;
        overflow: hidden;
        position: fixed;
        font-size: 40vw;
        text-align:center;
        }
    </style>""" + """
    <h1>{temp} °C</h1>
    """.format(temp=temperature)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)