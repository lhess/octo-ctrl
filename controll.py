#! /usr/bin/env python

# echo "@reboot /usr/bin/nice -n 19 /usr/bin/python ~/octo-ctrl/controll.py" >> mycron; crontab mycron;rm mycron

import os
import datetime
import sys
import RPi.GPIO as GPIO
import time
import subprocess
import json
import requests
import logging

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = BASE_PATH + "/.octo-ctrl-" + datetime.datetime.now().strftime('%Y%m%d') +  ".log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

###############################################################################

OCTOPRINT_API_KEY = "API KEY GOES HERE"

SHUTDOWN_PIN_BTN = 17
OCTOPRINT_STOP_PIN_BTN = 27
PIN_LED = 22

OCTOPRINT_API_HEADERS = {"X-Api-Key": OCTOPRINT_API_KEY, "Content-Type": "application/json"}
OCTOPRINT_API_URL = "http://127.0.0.1/api/job"

###############################################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SHUTDOWN_PIN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(OCTOPRINT_STOP_PIN_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Status LED
if (PIN_LED != False):
    GPIO.setup(PIN_LED, GPIO.OUT)
    GPIO.output(PIN_LED, 1)

timeStmp = time.time()

def shutdownButtonDown(channel):
    global timeStmp
    timeNow = time.time()
    if (timeNow - timeStmp) >= 0.3:
        logging.info("Shutdown System")

        subprocess.call(["sudo shutdown -h now"], shell=True)
        subprocess.call(["poweroff"], shell=True)

def octoprintStopButtonDown(channel):
    global timeStmp
    timeNow = time.time()
    if (timeNow - timeStmp) >= 0.3:
        s = requests.Session()
        r = json.loads((requests.get(OCTOPRINT_API_URL, headers=OCTOPRINT_API_HEADERS)).content)["state"]
        logging.debug(r)
        if r == "Printing":
            logging.info("Stop current print job")

            contents = json.dumps({"command": "cancel"})
            requests.post(OCTOPRINT_API_URL, data=contents, headers=OCTOPRINT_API_HEADERS)

GPIO.add_event_detect(SHUTDOWN_PIN_BTN, GPIO.FALLING, callback=shutdownButtonDown, bouncetime=300)
GPIO.add_event_detect(OCTOPRINT_STOP_PIN_BTN, GPIO.FALLING, callback=octoprintStopButtonDown, bouncetime=300)

try:
    print("Starting octo-ctrl, logging to " + LOG_FILE)
    logging.info("Starting octo-ctrl ...")
    while True:
        time.sleep(1)
finally:
    GPIO.cleanup()
