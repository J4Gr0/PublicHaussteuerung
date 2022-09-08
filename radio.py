from datetime import timedelta

import logging

import dataBase as db

class Radio:
    DEBUG = False

    RADIO_PRESS_INTERVALL = 4000
    RADIO_RUNTIME_SHORT = 5000 if DEBUG == True else 20 * 60 * 1000 # 20 Minuten
    RADIO_RUNTIME_LONG = 10000 if DEBUG == True else 40 * 60 * 1000 # 40 Minuten

    START_RADIO_SHORT = "RadioShort"
    START_RADIO_LONG = "RadioLong"
    STOP_RADIO = "StopRadio"

    def __init__(self):
        self.radioStopTime = db.TIME_FOR_COMP
        self.radioIsOn = False

    def startRadio(self, inOut, currentTime, duration):
        logging.info("   -   RADIO START Duration: {}".format(duration))
        self.radioStopTime = currentTime + timedelta(milliseconds=duration)
        self.radioIsOn = True
        inOut.activateRadio()

    def stopRadio(self, inOut):
        logging.info("   -   RADIO STOP")
        self.radioStopTime = db.TIME_FOR_COMP
        self.radioIsOn = False
        inOut.deactivateRadio()