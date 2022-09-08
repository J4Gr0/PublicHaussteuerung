from datetime import timedelta, datetime

import csv
import logging

import dataBase as db

class Pump:
    DEBUG = False

    UP_TO_DATE = "0"
    NEED_TO_UPDATE = "1"

    PUMP_RUNTIME = 5000 if DEBUG == True else 3 * 60 * 1000 #3 Minuten
    PUMP_INTERVALL_FOR_NEXT_RUN = 15 * 60 * 1000 #Only run after 15 Minutes

    START_PUMP = "StartPump"
    STOP_PUMP = "StopPump"
    
    def __init__(self):
        self.pumpTime = {"0": ["17:28", "checked", self.UP_TO_DATE], "1":["06:30", "checked", self.UP_TO_DATE], "2":["06:30", "checked", self.UP_TO_DATE], 
                        "3":["06:30", "checked", self.UP_TO_DATE], "4":["06:30", "checked", self.UP_TO_DATE], "5":["08:00", "checked", self.UP_TO_DATE], 
                        "6":["12:00", "checked", self.UP_TO_DATE]}

        self.pumpPressTimeStamp = db.TIME_FOR_COMP
        self.pumpStopTime = db.TIME_FOR_COMP
        self.pumpIsOn = False
        self.pumpShouldRunToday = self.getTodayPumpTime(datetime.now()) > datetime.now()

        #So you can start right at beginning
        self.lastTimeRunned = datetime.now() - timedelta(milliseconds=self.PUMP_INTERVALL_FOR_NEXT_RUN) 

    def startPump(self, inOut, currentTime):
        #Überprüfen, ob die Pumpe in den letzten X Minuten bereits lief, wenn ja, Pumpe nicht Starten
        if (self.lastTimeRunned + timedelta(milliseconds=self.PUMP_INTERVALL_FOR_NEXT_RUN)) < currentTime:
            logging.info("   -   PUMP START")
            self.pumpStopTime = currentTime + timedelta(milliseconds=self.PUMP_RUNTIME)
            self.pumpIsOn = True
            inOut.activatePump()
        else:
            logging.info("   -   PUMP Cannot start, 30 min not over")
            logging.info(self.lastTimeRunned.strftime("%Y-%m-%d %H:%M:%S"))
            inOut.showPumpNotRunAgain()

    def stopPump(self, inOut):
        logging.info("   -   PUMP STOP")
        self.pumpStopTime = db.TIME_FOR_COMP
        self.pumpIsOn = False
        inOut.deactivatePump()

    def getTodayPumpTime(self, currentTime):
        """"in datetime format"""
        temp = self.pumpTime[str(currentTime.weekday())][0]
        return currentTime.replace(hour=int(temp[0:2]), minute=int(temp[3:5]), second=0)

#-----File
    def writePumpTimeToTextFile(self):
        try:
            with open("pumpTime.csv", "w") as file:
                writer = csv.writer(file)
                writer.writerow(["day", "time", "doItThatDay?", "NeedToUpdate?"])
                rowToWrite = []
                for key, value in self.pumpTime.items():
                    rowToWrite.append(str(key))
                    rowToWrite.append(value[0])
                    rowToWrite.append(value[1])
                    rowToWrite.append(value[2])
                    writer.writerow(rowToWrite)
                    rowToWrite.clear()

        except BaseException as e:
            logging.error("     - Error WritePumpTimeToTextFile")
            logging.error(e)


    def writeTextFileToPumpTime(self):
        try:
            with open("pumpTime.csv", "r") as file:
                reader = csv.reader(file)                
                next(reader, None)
                
                for row in reader:
                    #row[0] dayIndex
                    self.pumpTime[row[0]] = [row[1], row[2], row[3]]

        except BaseException as e:
            logging.error("     - Error WriteTextFileToPumpTime")
            logging.error(e)