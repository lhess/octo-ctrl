#! /usr/bin/env python

# cd ~; git clone https://github.com/lhess/octo-ctrl.git
# sudo apt install -y python-requests python-gpiozero
# echo "@reboot /usr/bin/nice -n 19 /usr/bin/python ~/octo-ctrl/controll.py" >> mycron; crontab mycron; rm mycron
# sudo reboot

import os
import datetime
import sys
import time
import subprocess
import json
import requests
import logging
from gpiozero import Button
from gpiozero import LED

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = BASE_PATH + "/.octo-ctrl-" + datetime.datetime.now().strftime('%Y%m%d') +  ".log"

logging.basicConfig(
    filename = LOG_FILE,
    level = logging.DEBUG,
    format = "%(asctime)s | %(levelname)s | %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S"
)

###############################################################################

OCTOPRINT_API_KEY = "API KEY GOES HERE"

SHUTDOWN_BTN_PIN = 17
OCTOPRINT_STOP_BTN_PIN = 27
ON_LED_PIN = 22

OCTOPRINT_API_HEADERS = {"X-Api-Key": OCTOPRINT_API_KEY, "Content-Type": "application/json"}
OCTOPRINT_API_URL = "http://127.0.0.1/api/job"

###############################################################################

SHUTDOWN_BTN = Button(SHUTDOWN_BTN_PIN, pull_up = True, bounce_time = 0.3, hold_time = 2.0, hold_repeat = False)
OCTOPRINT_STOP_BTN = Button(OCTOPRINT_STOP_BTN_PIN, pull_up = True, bounce_time = 0.3, hold_time = 2.0, hold_repeat = False)

# Status LED
if (ON_LED_PIN != False):
    ON_LED = LED(ON_LED_PIN)
    ON_LED.on()

def shutdownSystem(channel):
    logging.info("Shutdown System")

    subprocess.call(["sudo shutdown -h now"], shell=True)
    subprocess.call(["poweroff"], shell=True)

def octoprintStopPrint(channel):
    s = requests.Session()
    r = json.loads((requests.get(OCTOPRINT_API_URL, headers=OCTOPRINT_API_HEADERS)).content)["state"]
    logging.debug(r)

    if r == "Printing":
        logging.info("Stop current print job")

        contents = json.dumps({"command": "cancel"})
        requests.post(OCTOPRINT_API_URL, data=contents, headers=OCTOPRINT_API_HEADERS)

SHUTDOWN_BTN.when_held = shutdownSystem
OCTOPRINT_STOP_BTN.when_held = octoprintStopPrint

try:
    print("Starting octo-ctrl, logging to " + LOG_FILE)
    logging.info("Starting octo-ctrl ...")
    while True:
        time.sleep(1)
finally:
     logging.info("Shuttiing down octo-ctrl ...")
