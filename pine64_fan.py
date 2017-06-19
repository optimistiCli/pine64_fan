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
import os
import sys


CPU_TEMP_PATH = '/sys/devices/virtual/thermal/thermal_zone0/temp'
GPU_TEMP_PATH = '/sys/devices/1c40000.gpu/dvfs/tempctrl'
STATE_PATH = '/sys/devices/virtual/thermal/cooling_device0/cur_state'
LOG_PATH = '/var/log/pine64_fan.log'
PID_PATH = '/var/run/pine64_fan.pid'
PIN_NUMBER = 23
TEMP_OFF = 47
TEMP_ON = 62


rotating = False
low_mid_temp = (TEMP_OFF + TEMP_ON) / 2
high_mid_temp = low_mid_temp + 1


def should_start(cpu_temp, gpu_temp, state):
	if state > 0:
		return True

	higher_temp = max(cpu_temp, gpu_temp)

	if higher_temp < high_mid_temp:
		return False

	if higher_temp > TEMP_ON:
		return True

	return random.randint(0,101) <= 100 * (higher_temp - high_mid_temp) / (TEMP_ON - high_mid_temp)

def should_stop(cpu_temp, gpu_temp, state):
	if state > 0:
		return False

	higher_temp = max(cpu_temp, gpu_temp)

	if higher_temp > low_mid_temp:
		return False

	if higher_temp < TEMP_OFF:
		return True

	return random.randint(0,101) <= 100 - 100 * (higher_temp - TEMP_OFF) / (low_mid_temp - TEMP_OFF)

def rotation_on():
	global rotating

	GPIO.output(PIN_NUMBER, True)
	rotating = True

def rotation_off():
	global rotating

	GPIO.output(PIN_NUMBER, False)
	rotating = False

def report(on_off, cpu_temp, gpu_temp, state):
	logging.info('Fan %s with CPU %i C / %i GPU %i C' % (
			'ON' if on_off else 'OFF',
			cpu_temp,
			state,
			gpu_temp
			))

def write_pid_file():
	pid = str(os.getpid())
	pid_file = open(PID_PATH, 'w')
	pid_file.write(pid)
	pid_file.close()

def remove_pid_file():
	os.remove(PID_PATH)

def finish(reason):
	logging.info('Finishing pine64 fan controller due to %s' % reason)
	rotation_off()
	GPIO.cleanup()
	remove_pid_file()
	quit()

def on_sigterm(signum, frame):
	finish('sigterm')

def already_running():
	return os.path.exists(PID_PATH)

def get_gpu_temp():
	gpu_temp_file = open(GPU_TEMP_PATH)
	gpu_temp = int(gpu_temp_file.read().split()[-1])
	gpu_temp_file.close()

	return gpu_temp

def run():
	if already_running():
		sys.exit('Can not run more then 1 instance')

	logging.basicConfig(
			format='%(asctime)s\t%(message)s',
			filename=LOG_PATH,
			level=logging.INFO
			)

	logging.info(
			'Starting pine64 fan controller for pin %i with on/off temperatures %i/%i Celsius'
			% (PIN_NUMBER, TEMP_ON, TEMP_OFF)
			)

	write_pid_file()

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN_NUMBER, GPIO.OUT)

	rotation_off()

	signal.signal(signal.SIGTERM, on_sigterm)

	try:
		while True:
			cpu_temp_file = open(CPU_TEMP_PATH)
			cpu_temp = int(cpu_temp_file.read())
			cpu_temp_file.close()

			state_file = open(STATE_PATH)
			state = int(state_file.read())
			state_file.close()

			gpu_temp = get_gpu_temp()

			if rotating and should_stop(cpu_temp, gpu_temp, state):
				rotation_off()
				report(False, cpu_temp, gpu_temp, state)
			elif not rotating and should_start(cpu_temp, gpu_temp, state):
				rotation_on()
				report(True, cpu_temp, gpu_temp, state)

			sleep(1)
	except KeyboardInterrupt:
		finish('user interrupt')
	except Exception as e:
		finish('an exception: %s' % e)

	finish('natural causes')


if __name__ == "__main__":
	run()
