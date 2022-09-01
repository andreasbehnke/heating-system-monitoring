#!/bin/bash
sudo apt install rpi.gpio-common python3-systemd python3-influxdb
sudo mkdir -p /opt/gasmeter
sudo cp gasmeter.py /opt/gasmeter
sudo chmod 0700 /opt/gasmeter/gasmeter.py
sudo cp gasmeter.service /etc/systemd/system
sudo cp gasmeter_template.ini /etc/gasmeter.ini
sudo chmod 0600 /etc/gasmeter.ini
sudo mkdir -p /var/lib/gasmeter
sudo touch /var/lib/gasmeter/gasmeter.dat
sudo systemctl enable gasmeter