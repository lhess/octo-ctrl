#! /usr/bin/env python

# echo "@reboot /usr/bin/nice -n 19 /usr/bin/python ~/octo-ctrl/controll.py" >> mycron; crontab mycron;rm mycron

import os
import RPi.GPIO as GPIO
import time
import subprocess

PIN_BTN = 17
PIN_LED = 22

GPIO.setmode(GPIO.BCM)

# Button for shutdown
GPIO.setup(PIN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Status LED
GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.output(PIN_LED, 1)

timeStmp = time.time()

def buttonDown(channel):
    global timeStmp
    timeNow = time.time()
    if (timeNow - timeStmp) >= 0.3:
        subprocess.call(['sudo shutdown -h now'], shell=True)
        subprocess.call(['poweroff'], shell=True)

GPIO.add_event_detect(PIN_BTN, GPIO.FALLING, callback=buttonDown, bouncetime=300)

try:
    while True:
        time.sleep(1)
finally:
    GPIO.cleanup()
