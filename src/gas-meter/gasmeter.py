#!/usr/bin/python
# read gas meter impulses from GPIO pin 23 send time series data to influxdb.
# Reed contact must switch pin to GND, the internal pull up resistor will be used.

import configparser
import logging
import time
from systemd.journal import JournalHandler

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
count_file = config['general']['count_file']
measurement_delta_time = int(config['general']['measurement_delta_time'])
impulse_increment = float(config['general']['impulse_increment'])
channel = int(config['general']['gpio_pin'])  # connect GPIO pin to reed contact, other end of reed contact to GND.
influx_measurement_name = config['general']['influx_measurement_name']
influx_port = int(config['general']['influx_port'])
influx_host = config['general']['influx_host']
influx_user = config['general']['influx_user']
influx_pass = config['general']['influx_pass']
influx_database = config['general']['influx_database']

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
time.sleep(2)

log = logging.getLogger('gasmeter')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_database)

delta_time = measurement_delta_time
impulse = not GPIO.input(channel)  # retrieve the current pulse state

while True:
    try:
        if not GPIO.input(channel) and not impulse:
            impulse = True  # we are now within the pulse (duration around 4 seconds, or gas meter may also stop in this position)
            gas_value = read_actual()
            gas_value = gas_value + impulse_increment
            write_actual(gas_value)
            delta_time = 0  # trigger send if counter changes
        elif GPIO.input(channel) and impulse:
            impulse = False
        if delta_time == 0:
            send_actual()
            delta_time = measurement_delta_time  # send at least once per delta time
        delta_time = delta_time - 1
        time.sleep(1)
    except:
        log.exception("Exception in main thread, retry")
        delta_time = measurement_delta_time
