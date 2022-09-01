# Heating System Monitoring
Documentation and scripts of my home heating system monitoring. I use this tooling to identify potential gas savings. The gas system has never been fine tuned after installation.
I use the following software for home automation and monitoring, your system may vary:

* iobroker as middleware
* influxdb (1.8+) as time series database
* grafana for analysis and graphs

This document describes the software and hardware to collect internal machine data of a viessmann gas boiler and gas meter counter. The directory src/gas-meter contains a python daemon which will
listen to changes on 

# Heating Hardware

* viessmann vitodens 222-F BS2B 2.4 - 26.0 kW
* gas meter 

# Monitoring Hardware

* raspberry pi 3b
* viessmann optolink USB cable
* reed contact to count gas meter impulses

# Monitoring Software - vonctrold

The service [vcontrold](https://github.com/openv/vcontrold) is used to collect system data via [usb optolink cable](https://github.com/openv/openv/wiki/Die-Optolink-Schnittstelle).

Setup SSH public key and pi user login using rpi imager tool. Boot raspberry pi for the first time.

prevent autologin

* `sudo raspi-config nonint do_boot_behaviour B1`

update packages

* `sudo apt update && sudo apt upgrade`

install packages

* `sudo apt install git automake autoconf build-essential cmake libxml2-dev`

build software

* `git clone https://github.com/openv/vcontrold.git`
* `cd vcontrold`
* `mkdir build`
* `cd build`
* `cmake -DMANPAGES=OFF ..`
* `make`
* `sudo make install`

copy configuration

`sudo mkdir /etc/vcontrold`

`sudo mv vcontrold.xml vito.xml /etc/vcontrold/`

install systemd service

* `/etc/systemd/system/vcontrold.service`:

```
[Unit]
Description=vcontrold daemon
After=syslog.target systemd-udev-settle.service
 
[Service]
Type=forking
ExecStartPre=/bin/ls /dev/bus/usb/001
ExecStart=/usr/sbin/vcontrold
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=120
StandardOutput=null
 
[Install]
WantedBy=multi-user.target
```

* `sudo systemctl start vcontrold`
* `sudo systemctl enable vcontrold`

# Monitoring Software - gas meter counter

Install service which will write gas metric to influx db. For simplicity I skip the iobroker middleware here, writing time series directly. A better approach would be to use mqtt here, but I do not need this data in iobroker, so no use for this extra complexity.

prepare hardware

* add reed contact to gasmeter https://wiki.volkszaehler.org/hardware/channels/meters/gas
* connect reed contact to GND and an unused GPIO pin of the raspberry pi, e.g. pin GPIO 23.

install service

* `git clone https://github.com/andreasbehnke/heating-system-monitoring.git`
* `cd heating-system-monitoring/src/gas-meter`
* `./install.sh`

configure service

* edit file /var/lib/gasmeter/gasmeter.dat, set your actual gas counter. Ignore the last decimal place, because this wheel contains the magnet which triggers the reed contact!
* edit file /etc/gasmeter.ini

start service

* start service with `sudo systemctl start gasmeter.service`
* watch for erros `journalctl -f`
