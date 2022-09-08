from datetime import datetime
import logging
import csv

class HouseTime:

    def __init__(self):
        #nur die Zeiten die angezeigt werden
        self.houseTimes = {"0":["08:00", "22:00"],"1":["08:00", "22:00"],"2":["08:00", "22:00"],"3":["08:00", "22:00"],"4":["08:00", "22:00"],
        "5":["08:00", "22:00"],"6":["08:00", "22:00"]}

        self.realTodayUpTime = "08:00"
        self.realTodayDownTime = "22:00"

        self.offSetMorning = 0
        self.offSetEvening = 0

    #in datetime format
    def getTodayUpTime(self, currentTime):
        return self.houseTimes[str(currentTime.weekday())][0]

    def getTodayDownTime(self, currentTime):
        return self.houseTimes[str(currentTime.weekday())][1]

    def setUpTime(self, currentTime, upTimeStr, weekDayIndex):
        #upTime in Datettime format casten
        upTime = currentTime.replace(hour=int(upTimeStr[0:2]), minute=int(upTimeStr[3:5]), second=0)
        checkCorrectTime = True
        checkCorrectTime = checkCorrectTime and (upTime > currentTime.replace(hour=0, minute=0, second=0))
        checkCorrectTime = checkCorrectTime and (upTime < currentTime.replace(hour=14, minute=59, second=0))

        #Falls nicht die korrekte Zeit ist, Standardzeit
        if checkCorrectTime:
            self.houseTimes[str(weekDayIndex)][0] = upTimeStr
        else:
            self.houseTimes[str(weekDayIndex)][0] = "08:00"

    def setDownTime(self, currentTime, downTimeStr, weekDayIndex):
        #downTime in Datetimeformat casten
        downTime = currentTime.replace(hour=int(downTimeStr[0:2]), minute=int(downTimeStr[3:5]), second=0)
        checkCorrectTime = True
        checkCorrectTime = checkCorrectTime and (downTime > currentTime.replace(hour=15, minute=0, second=0))
        checkCorrectTime = checkCorrectTime and (downTime < currentTime.replace(hour=23, minute=59, second=0))

        #Falls nicht die korrekte Zeit ist, Standardzeit
        if checkCorrectTime:
            self.houseTimes[str(weekDayIndex)][1] = downTimeStr
        else:
            self.houseTimes[str(weekDayIndex)][1] = "22:00"


    def writeHouseTimeToTextFile(self):
        try:
            with open("houseTime.csv", "w") as file:
                writer = csv.writer(file)
                writer.writerow(["day", "sunrise", "sunset"])
                rowToWrite = []
                for key, value in self.houseTimes.items():
                    rowToWrite.append(str(key))
                    rowToWrite.append(value[0]) #upTime
                    rowToWrite.append(value[1]) #downTime
                    writer.writerow(rowToWrite)
                    rowToWrite.clear()

        except BaseException as e:
            logging.info("Error HouseTimeToTextFile")
            logging.info(e)


    def writeTextFileToHouseTime(self):
        try:
            with open("houseTime.csv", "r") as file:
                reader = csv.reader(file)
                next(reader, None)
                for row in reader:
                    self.houseTimes[row[0]] = [row[1], row[2]]

        except BaseException as e:
            logging.info("Error writeTextFileToHouseTime")
            logging.info(e)
