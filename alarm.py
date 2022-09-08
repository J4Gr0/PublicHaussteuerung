from mail import Mail

from datetime import timedelta

import logging

import dataBase as db

class Alarm:

    START_ALARM = "StartAlarm"
    STOP_ALARM = "StopAlarm"
    ALARM_SIGNAL_ON_TIME = 5000 #ms

    def __init__(self):
        self.alarmIsOn = False
        self.alarmCanStart = False
        self.alarmSignalAlreadyTriggerd = False
        self.alarmStopTime = db.TIME_FOR_COMP
        self.myMail = Mail()

        self.__stoppedAlarmSignal = False

    def startAlarm(self):
        logging.info("     -   ALARM START")
        self.alarmCanStart = False
        self.alarmIsOn = True
        self.alarmSignalAlreadyTriggerd = False

        self.__stoppedAlarmSignal = False

    def stopAlarm(self, inOut, currentTime):
        logging.info("     -   ALARM STOP")
        self.alarmIsOn = False
        self.alarmCanStart = False
        self.alarmSignalAlreadyTriggerd = False
        self.stopAlarmSignal(inOut, currentTime)

    def triggerAlarmSignal(self, inOut, currentTime):
        logging.info("     - Window Open, Start Alarm Signal")
        try:
            self.myMail.sendMail()  
            logging.info("     - e-Mail versendet")
        except BaseException as e:
            logging.error("     - Konnte e-Mail nicht versenden")
            logging.error(e)

        self.alarmStopTime = currentTime + timedelta(milliseconds = self.ALARM_SIGNAL_ON_TIME )
        self.alarmSignalAlreadyTriggerd = True
        inOut.activateAlarmSignal()

    def stopAlarmSignal(self, inOut, currentTime):
        #Überprüfen, ob es nicht schon gestoppt wurde
        if not self.__stoppedAlarmSignal:
            logging.info("     - Stop Alarm Signal")
            self.alarmStopTime = db.TIME_FOR_COMP
            inOut.deactivateAlarmSignal()
            self.__stoppedAlarmSignal = True


    def checkAlarmCanStart(self, inOut):
        #Achtung NOT
        #Wenn ein Zimmer offen ist, kann die Alarmanlage nicht gestartet werden
        self.alarmCanStart = not self.isOneWindowOpen(inOut)
        return self.alarmCanStart

    def isOneWindowOpen(self, inOut):
        if inOut.isTerraRightWindowOpen() or inOut.isOtherWindowOpen():
            return True
        else:
            return False