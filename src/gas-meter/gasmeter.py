#!/usr/bin/python
# read gas meter impulses from GPIO pin 23 and send time series data to influxdb.
# Reed contact must switch pin 23 to GND, the internal pull up resistor will be used.
#
# Usage: gasmeter.py INFLUX_HOST INFLUX_USER_NAME INFLUX_USER_PASS INFLUX_DB_NAME

import sys
import time
from influxdb import InfluxDBClient
import RPi.GPIO as GPIO

def readActual():
	file = open('gasmeter.dat')
	line = file.read()
	file.close()
	a = float(line)
	return a
def writeActual(a):
	file = open('gasmeter.dat', 'w')
	s = '{0:0.2f}'.format(a)
	file.write(s)
	file.close()
def sendActual(client):
	json_body = [{
        "measurement": "heating_system_gas_meter_count",
        "fields": {
            "value": readActual()
        }
    }]
	client.write_points(json_body)

channel = 23 # connect GPIO 23 to reed contact, other end of reed contact to GND.
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down = GPIO.PUD_UP)
time.sleep(2)

client = InfluxDBClient(sys.argv[1], 8086, sys.argv[2], sys.argv[3], sys.argv[4])

seconds = 60
impulse = not GPIO.input(channel) # retrieve the current pulse state

while True:
	if not GPIO.input(channel) and not impulse:
		impulse = True # we are now within the pulse (duration around 4 seconds, or gas meter may also stop in this position)
		gas_value = readActual()
		gas_value = gas_value + 0.01
		writeActual(gas_value)
		seconds = 0 # trigger send if counter changes
	elif GPIO.input(channel) and impulse:
		impulse = False
	if seconds == 0:
		sendActual(client)
		seconds = 60 # send once per minute
	seconds = seconds - 1
	time.sleep(1)
