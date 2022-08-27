#!/usr/bin/python
# read gas meter impulses from GPIO pin 23 and send time series data to influxdb.
# Reed contact must switch pin 23 to GND, the internal pull up resistor will be used.
#
# Usage: gasmeter.py INFLUX_HOST INFLUX_USER_NAME INFLUX_USER_PASS INFLUX_DB_NAME

import configparser
import logging
import time
from systemd.journal import JournaldLogHandler

from influxdb import InfluxDBClient
import RPi.GPIO as GPIO


def read_actual():
    file = open(count_file)
    line = file.read()
    file.close()
    a = float(line)
    return a


def write_actual(a):
    file = open(count_file, 'w')
    s = '{0:0.2f}'.format(a)
    file.write(s)
    file.close()


def send_actual():
    json_body = [{
        "measurement": influx_measurement_name,
        "fields": {
            "value": read_actual()
        }
    }]
    client.write_points(json_body)


# read configuration
config = configparser.ConfigParser()
config.read('/etc/gasmeter.ini')
count_file = config['DEFAULT', 'count_file']
measurement_delta_time = int(config['DEFAULT', 'measurement_delta_time'])
impulse_increment = config['DEFAULT', 'impulse_increment']
channel = int(config['DEFAULT', 'gpio_pin'])  # connect GPIO pin to reed contact, other end of reed contact to GND.
influx_measurement_name = config['DEFAULT', 'influx_measurement_name']
influx_port = config['DEFAULT', 'influx_port']
influx_host = config['DEFAULT', 'influx_host']
influx_user = config['DEFAULT', 'influx_user']
influx_pass = config['DEFAULT', 'influx_pass']
influx_database = config['DEFAULT', 'influx_database']

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
time.sleep(2)

log = logging.getLogger('gasmeter')
log.addHandler(JournaldLogHandler())
log.setLevel(logging.INFO)

client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_database)

seconds = measurement_delta_time
impulse = not GPIO.input(channel)  # retrieve the current pulse state

while True:
    try:
        if not GPIO.input(channel) and not impulse:
            impulse = True  # we are now within the pulse (duration around 4 seconds, or gas meter may also stop in this position)
            gas_value = read_actual()
            gas_value = gas_value + impulse_increment
            write_actual(gas_value)
            seconds = 0  # trigger send if counter changes
        elif GPIO.input(channel) and impulse:
            impulse = False
        if seconds == 0:
            send_actual(client)
            seconds = measurement_delta_time  # send at least once per delta time
        seconds = seconds - 1
        time.sleep(1)
    except:
        log.exception("Exception in main thread, retry")
        seconds = measurement_delta_time
