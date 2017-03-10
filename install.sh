#!/bin/bash

if [ $(id -u) -ne 0 ] ; then
	echo Please run as root
	exit 1
fi

cat pine64_fan.py > /usr/local/bin/pine64_fan.py
chmod 755 /usr/local/bin/pine64_fan.py

cat pine64_fan.service > /lib/systemd/system/pine64_fan.service
chmod 644 /lib/systemd/system/pine64_fan.service

systemctl daemon-reload
systemctl enable pine64_fan.service
