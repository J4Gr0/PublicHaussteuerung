from datetime import timedelta

import logging

import dataBase as db

class Fan:
    DEBUG = False

    FAN_PRESS_INTERVALL = 2000
    FAN_RUNTIME_SHORT = 5000 if DEBUG == True else 20 * 60 * 1000 # 20 Minuten
    FAN_RUNTIME_LONG = 10000 if DEBUG == True else 40 * 60 * 1000 # 40 Minuten

    START_FAN_SHORT = "FanShort"
    START_FAN_LONG = "FanLong"
    STOP_FAN = "FanStop"

    def __init__(self):
        self.fanPressTimeStamp = db.TIME_FOR_COMP
        self.fanPressTimeDuration = timedelta(milliseconds=0)
        self.fanStopTime = db.TIME_FOR_COMP
        self.fanIsOn = False

    def startFan(self, inOut, currentTime, duration):
        logging.info("   -   FAN START Duration: {}".format(duration))
        self.fanStopTime = currentTime + timedelta(milliseconds=duration)
        self.fanIsOn = True
        self.fanPressTimeDuration = db.TIME_FOR_COMP
        inOut.activateFan()

    def stopFan(self, inOut):
        logging.info("   -   FAN STOP")
        self.fanStopTime = db.TIME_FOR_COMP
        self.fanIsOn = False
        self.fanPressTimeDuration = db.TIME_FOR_COMP
        inOut.deactivateFan()