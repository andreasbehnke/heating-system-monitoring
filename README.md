# Heating System Monitoring
Documentation and scripts of my home heating system monitoring. I use this tooling to identify potential gas savings. The gas system has never been fine tuned after installation.

# Heating Hardware

* viessmann vitodens 222-F BS2B 2.4 - 26.0 kW
* gas meter 

# Monitoring Hardware

* raspberry pi 3b
* viessmann optolink USB cable
* reed contact to count gas meter impulses

# Monitoring Software

## vcontrold

The service vcontrold is used to collect system data via usb optolink cable.

## gas meter counter

* sudo apt install rpi.gpio-common 
* sudo apt install python3-influxdb 