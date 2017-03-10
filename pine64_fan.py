#!/usr/bin/python

# Basic pine64 fan controller based on schematics by MarkHaysHarris777
# found at the pine64 forum http://forum.pine64.org/showthread.php?tid=1854

# You can use this script in any manner that suits you though remember at all 
# times that by using it you agree that you use it at your own risk and neither 
# I nor anybody else except for yourself is to be held responsible in case 
# anything goes wrong as a result of using this script.


from time import sleep
import RPi.GPIO as GPIO
import random
import signal
import logging


TEMP_PATH = '/sys/devices/virtual/thermal/thermal_zone0/temp'
STATE_PATH = '/sys/devices/virtual/thermal/cooling_device0/cur_state'
LOG_PATH = '/var/log/pine64_fan.log'
PIN_NUMBER = 23
TEMP_OFF = 47
TEMP_ON = 62


rotating = False
low_mid_temp = (TEMP_OFF + TEMP_ON) / 2
high_mid_temp = low_mid_temp + 1


def should_start(temp, state):
	if state > 0:
		return True

	if temp < high_mid_temp:
		return False

	if temp > TEMP_ON:
		return True

	return random.randint(0,101) <= 100 * (temp - high_mid_temp) / (TEMP_ON - high_mid_temp)

def should_stop(temp, state):
	if state > 0:
		return False

	if temp > low_mid_temp:
		return False

	if temp < TEMP_OFF:
		return True

	return random.randint(0,101) <= 100 - 100 * (temp - TEMP_OFF) / (low_mid_temp - TEMP_OFF)

def rotation_on():
	global rotating

	GPIO.output(PIN_NUMBER, True)
	rotating = True

def rotation_off():
	global rotating

	GPIO.output(PIN_NUMBER, False)
	rotating = False

def report(on_off, temp, state):
	logging.info('Fan %s at %i Celsius with CPU state %i' % (
			'ON' if on_off else 'OFF',
			temp,
			state
			))

def finish(reason):
	logging.info('Finishing pine64 fan controller due to %s' % reason)
	rotation_off()
	GPIO.cleanup()
	quit()

def on_sigterm(signum, frame):
	finish('sigterm')


def run():
	logging.basicConfig(
			format='%(levelname)s:%(message)s',
			filename=LOG_PATH,
			level=logging.INFO
			)

	logging.info(
			'Starting pine64 fan controller for pin %i with on/off temperatures %i/%i Celsius'
			% (PIN_NUMBER, TEMP_ON, TEMP_OFF)
			)

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN_NUMBER, GPIO.OUT)

	rotation_off()

	signal.signal(signal.SIGTERM, on_sigterm)

	try:
		while True:
			temp_file = open(TEMP_PATH)
			temp = int(temp_file.read())
			temp_file.close()

			state_file = open(STATE_PATH)
			state = int(state_file.read())
			state_file.close()

			if rotating and should_stop(temp, state):
				rotation_off()
				report(False, temp, state)
			elif not rotating and should_start(temp, state):
				rotation_on()
				report(True, temp, state)

			sleep(1)
	except KeyboardInterrupt:
		finish('user interrupt')
	except Exception as e:
		finish('an exception: %s' % e)

	finish('natural causes')


if __name__ == "__main__":
	run()
