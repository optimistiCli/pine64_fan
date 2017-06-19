#!/bin/bash

if [ $(id -u) -ne 0 ] ; then
	echo Please run as root
	exit 1
fi


# file name, destination dir, mode
install_file() {
	d="$2"/"$1"
	cat "$1" > "$d"
	chmod "$3" "$d"
}

echo Checking prerequisites

if ! python -c 'import RPi.GPIO' 2>/dev/null ; then
	echo Please install RPi.GPIO python module
	exit 2
fi

if ! systemctl 2>/dev/null | grep -qe '-\.mount' ; then
	echo Please make sure your system uses systemd
	exit 3
fi


if systemctl is-enabled pine64_fan.service 2>/dev/null 1>/dev/null ; then 
	echo Stopping pine64_fan.service
	systemctl stop pine64_fan.service
	sleep 1
fi


echo Copying files
install_file pine64_fan.py /usr/local/bin 755
install_file pine64_fan.service /lib/systemd/system 644
install_file pine64_monitor.sh /usr/local/bin 755

echo Starting pine64_fan.service

systemctl daemon-reload
sleep 1

systemctl enable pine64_fan.service
sleep 1

systemctl start pine64_fan.service
sleep 1
