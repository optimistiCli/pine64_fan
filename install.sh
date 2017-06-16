#!/bin/bash

if [ $(id -u) -ne 0 ] ; then
	echo Please run as root
	exit 1
fi

if ! python -c 'import RPi.GPIO' 2>/dev/null ; then
	echo Please install RPi.GPIO python module
	exit 2
fi

if ! systemctl 2>/dev/null | grep -qe '-\.mount' ; then
	echo Please make sure your system uses systemd
	exit 3
fi

cat pine64_fan.py > /usr/local/bin/pine64_fan.py
chmod 755 /usr/local/bin/pine64_fan.py

cat pine64_fan.service > /lib/systemd/system/pine64_fan.service
chmod 644 /lib/systemd/system/pine64_fan.service

systemctl daemon-reload
sleep 1

systemctl enable pine64_fan.service
sleep 1

systemctl start pine64_fan.service
sleep 1
