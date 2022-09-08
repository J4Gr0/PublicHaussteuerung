from datetime import datetime, timedelta
from random import randint

import logging

import dataBase as db

class Room:
    DEBUG = False
#-----Room Names for Comparison
    JAN = "jan"
    LEA_SLEEP = "leaSleeping"
    LEA_LIVING = "leaLiving"
    PARENTS = "parents"
    TOILET = "toilet"
    GUEST_TOILET = "guestToilet"
    KITCHEN = "kitchen"
    TERRA_RIGHT = "terraRight"
    TERRA_LEFT = "terraLeft"
    LIVING_GARAGE = "livingGarage"

#-----For Queue
    DOWN_JAN = "DownJan"
    DOWN_LEA_SLEEP = "DownLeaSleep"
    DOWN_LEA_LIVNG = "DownLeaLiving"
    DOWN_PARENTS = "DownParents"
    DOWN_TOILET = "DownToilet"
    DOWN_GUEST_TOILET = "DownGuestToilet"
    DOWN_KITCHEN = "DownKitchen"
    DOWN_TERRA_RIGHT = "DownTerraRight"
    DOWN_TERRA_LEFT = "DownTerraLeft"
    DOWN_LIVING_GARAGE = "DownLivingGarage"

    UP_JAN = "UpJan"
    UP_LEA_SLEEP = "UpLeaSleep"
    UP_LEA_LIVING = "UpLeaLiving"
    UP_PARENTS = "UpParents"
    UP_TOILET = "UpToilet"
    UP_GUEST_TOILET = "UpGuestToilet"
    UP_KITCHEN = "UpKitchen"
    UP_TERRA_RIGHT = "UpTerraRight"
    UP_TERRA_LEFT = "UpTerraLeft"
    UP_LIVING_GARAGE = "UpLivingGarage"

    UP_ALL = "UpAll"
    DOWN_ALL = "DownAll"

#-----all the ROLLSTATI
    ROLLSTATUS_IDLE = 0        
    ROLLSTATUS_ONE_SHOULD_UP = 1
    ROLLSTATUS_ONE_UP = 2
    ROLLSTATUS_ONE_SHOULD_DOWN = 3
    ROLLSTATUS_ONE_DOWN = 4
    ROLLSTATUS_TERRA_RIGHT_SHOULD_TRY = 5
    ROLLSTATUS_TERRA_RIGHT_TRY = 6
    ROLLSTATUS_TERRA_COMPLETE = 7   
    ROLLSTATUS_STOP = 8 
    ROLLSTATUS_CLEAR_COMMAND = 9

#-----Limits for Up and Down Time
    UP_LOWER_LIMIT = "00:00"
    UP_UPPER_LIMIT = "14:59"

    DOWN_LOWER_LIMIT = "15:00"
    DOWN_UPPER_LIMIT = "23:59"


#-----
    ROLLO_RUNTIME_LONG = 20 * 1000 if DEBUG == True else 35 * 1000 #35 Sec Wohnzimmer
    ROLLO_RUNTIME_SHORT = 15 * 1000 if DEBUG == True else 25 * 1000 #25 Sec alle anderen Zimmer

    MCP1 = 1
    MCP2 = 2

    DEFAULT_UP_TIME = "08:00"
    DEFAULT_DOWN_TIME = "22:00"
    RANDOM_RANGE = 15


#-----Funktions
    def __init__(self, name, bitUp, bitDown, mcpNr, rolldauer, upItemQueue, downItemQueue):
        self.name = name
        self.bitUp = bitUp
        self.bitDown = bitDown
        self.mcpNr = mcpNr
        self.rollDuration = rolldauer
        self.upItemQueue = upItemQueue
        self.downItemQueue = downItemQueue

        self.stopTime = db.TIME_FOR_COMP
        self.rollStatus = self.ROLLSTATUS_IDLE

        self.upWithClock = False
        self.upTime = self.DEFAULT_UP_TIME
        self.upTimeWebSite = self.DEFAULT_UP_TIME
        self.shouldUpToday = None
        self.gotOwnUpTime = "" #leer wegen checkbox
        self.allowUpToday = "checked" #wegen Checkbox

        self.downWithClock = False
        self.downTime = self.DEFAULT_DOWN_TIME
        self.downTimeWebSite = self.DEFAULT_DOWN_TIME
        self.shouldDownToday = None
        self.gotOwnDownTime = ""
        self.allowDownToday = "checked" #wegen Checkbox



    def setUpTimeParameters(self, webUpTime, onlyOneRoom, upTimeCheckBox, shouldUpCheckBox, randomNumber=0):
        currentTime = datetime.now()

        upTimeTemp = self.castStringTimeToDateTime(currentTime, webUpTime)
        self.gotOwnUpTime = upTimeCheckBox #Speicher ob individuelle Up Zeit
        self.allowUpToday = shouldUpCheckBox

        #Room got own upTime
        if onlyOneRoom:
            if self.checkForValidUpTime(upTimeTemp, currentTime):

                #nur wenn das Fenster alleine fahren soll, werden seperate Parameter gesetzt
                if self.gotOwnUpTime == "checked":
                    self.upTime = webUpTime #self.addRandomTime(upTimeTemp).strftime("%H:%S") #save randomTime for drive rollo
                    self.upTimeWebSite = webUpTime

                    if self.allowUpToday == "checked":
                        self.shouldUpToday = upTimeTemp > currentTime
                    else:
                        self.shouldUpToday = False
                else:
                    #Wenn die Checkbox nicht geklickt wurde, soll nur die anzuzeigende Zeit aktuallisiert werden
                    self.upTimeWebSite = webUpTime
                    self.upTime = db.houseTime.realTodayUpTime
                    
                    if self.allowUpToday == "checked":
                        self.shouldUpToday = self.castStringTimeToDateTime(currentTime, db.houseTime.realTodayUpTime) > currentTime
                    else:
                        self.shouldUpToday = False
            else:
                logging.info("    -Not a valid upTime (00:00 - 14.59)")
                #self.__setDefaultUpTimeValues(currentTime, upTimeCheckBox)

        #das Zimmer hat keine alleinstehende hochzeit, und wir als Einheit aktualisiert
        else:
            if self.checkForValidUpTime(upTimeTemp, currentTime):
                #nur wenn das Fenster alleine fahren soll, werden seperate Parameter gesetzt
                if not (self.gotOwnUpTime == "checked"):
                    #Wenn die Checkbox nicht geklickt wurde, soll nur die anzuzeigende Zeit aktuallisiert werden
                    self.upTime = (self.castStringTimeToDateTime(currentTime, webUpTime) + timedelta(minutes=randomNumber)).strftime("%H:%M")
                    db.houseTime.realTodayUpTime  = self.upTime
                    #Checkbox, ob überhaupt gefahren werden darf
                    if self.allowUpToday == "checked":
                        self.shouldUpToday = upTimeTemp > currentTime
                    else:
                        self.shouldUpToday = False
            else:
                logging.info("    -Not a valid upTime (00:00 - 14.59)")
                #self.__setDefaultUpTimeValues(currentTime, upTimeCheckBox

        logging.info("    -Name: {} UpTime: {} UpTimeWebSite: {} gotOwnUpTime: {} allowUpToday: {} shouldUp: {}"
                    .format(self.name, self.upTime, self.upTimeWebSite, self.gotOwnUpTime, self.allowUpToday, self.shouldUpToday))


    def setDownTimeParameters(self, webDownTime, onlyOneRoom, downTimeCheckBox, shouldDownCheckBox, randomNumber=0):
        currentTime = datetime.now()

        downTimeTemp = self.castStringTimeToDateTime(currentTime, webDownTime)
        self.gotOwnDownTime = downTimeCheckBox #Speicher ob individuelle Up Zeit
        self.allowDownToday = shouldDownCheckBox

        #Room got own upTime
        if onlyOneRoom:
            if self.checkForValidDownTime(downTimeTemp, currentTime):

                #nur wenn das Fenster alleine fahren soll, werden seperate Parameter gesetzt
                if self.gotOwnDownTime == "checked":
                    self.downTime = webDownTime #self.addRandomTime(upTimeTemp).strftime("%H:%S") #save randomTime for drive rollo
                    self.downTimeWebSite = webDownTime

                    #nur wenn das  Zimmer eine neue Rutnerfahrzeit bekommt, soll aktualisiert werden, ob es heute runterfahren soll
                    if self.allowDownToday == "checked":
                        self.shouldDownToday = downTimeTemp > currentTime
                    else:
                        self.shouldDownToday = False
                else:
                    #Wenn die Checkbox nicht geklickt wurde, soll nur die anzuzeigende Zeit aktuallisiert werden
                    self.downTimeWebSite = webDownTime
                    self.downTime = db.houseTime.realTodayDownTime
                    
                    if self.allowDownToday == "checked":
                        self.shouldDownToday = self.castStringTimeToDateTime(currentTime, db.houseTime.realTodayDownTime) > currentTime
                    else:
                        self.shouldDownToday = False
            else:
                logging.info("    -Not a valid downTime (15:00 - 23.59)")
                #self.__setDefaultDownTimeValues(currentTime, upTimeCheckBox)

        #das Zimmer hat keine alleinstehende runterZeit, und wir als Einheit aktualisiert
        else:
            if self.checkForValidDownTime(downTimeTemp, currentTime):
                #soll generell überhaupt hochfahren über die Checkboxen der Website

                #nur wenn das Fenster nicht alleine fahren soll, werden seperate Parameter gesetzt
                if not (self.gotOwnDownTime == "checked"):
                    #Wenn die Checkbox nicht geklickt wurde, soll nur die anzuzeigende Zeit aktuallisiert werden
                    self.downTime = (self.castStringTimeToDateTime(currentTime, webDownTime) + timedelta(minutes=randomNumber)).strftime("%H:%M")
                    db.houseTime.realTodayDownTime = self.downTime
                    
                    if self.allowDownToday == "checked":
                        self.shouldDownToday = downTimeTemp > currentTime
                    else:
                        self.shouldDownToday = False
            else:
                logging.info("    -Not a valid downTime (15:00 - 23.59)")
                #self.__setDefaultDownTimeValues(currentTime, upTimeCheckBox)

        logging.info("    -Name: {} downTime: {} downTimeWebSite: {} gotOwnDownTime: {} allowDownToday: {} shouldDown: {}"
                    .format(self.name, self.downTime, self.downTimeWebSite, self.gotOwnDownTime, self.allowDownToday, self.shouldDownToday))



    def __setDefaultUpTimeValues(self, currentTime, checkBoxValue):
        self.upTime = self.DEFAULT_UP_TIME
        self.upTimeToDisplay = self.DEFAULT_UP_TIME
        self.shouldUpToday = self.castStringTimeToDateTime(currentTime, self.DEFAULT_UP_TIME) > currentTime
        self.gotOwnUpTime = checkBoxValue

    def __setDefaultDownTimeValues(self, currentTime, checkBoxValue):
        self.downTime = self.DEFAULT_DOWN_TIME
        self.downTimeToDisplay = self.DEFAULT_DOWN_TIME
        self.shouldDownToday = self.castStringTimeToDateTime(currentTime, self.DEFAULT_DOWN_TIME) > currentTime
        self.gotOwnDownTime = checkBoxValue

    def addRandomTime(self, timeToChange):
        randNumber = randint(-self.RANDOM_RANGE, self.RANDOM_RANGE)
        return timeToChange + timedelta(minutes=randNumber)

    def castStringTimeToDateTime(self, currentTime, stringTime):
        return currentTime.replace(hour=int(stringTime[0:2]), minute=int(stringTime[3:5]), second=0)

    def checkForValidUpTime(self, toCheckTime, currentTime):
        returnValue = True
        returnValue = returnValue and (toCheckTime > self.castStringTimeToDateTime(currentTime, self.UP_LOWER_LIMIT))
        returnValue = returnValue and (toCheckTime < self.castStringTimeToDateTime(currentTime, self.UP_UPPER_LIMIT))
        return returnValue

    def checkForValidDownTime(self, toCheckTime, currentTime):
        returnValue = True
        returnValue = returnValue and (toCheckTime > self.castStringTimeToDateTime(currentTime, self.DOWN_LOWER_LIMIT))
        returnValue = returnValue and (toCheckTime < self.castStringTimeToDateTime(currentTime, self.DOWN_UPPER_LIMIT))
        return returnValue

#-----Rollo Drive
    def doMyRolloUp(self, inOut, currentTime, activeCounter):
        self.rollStatus = self.ROLLSTATUS_ONE_UP
        self.stopTime = currentTime + timedelta(milliseconds=self.rollDuration)
        inOut.doRolloUp(self.mcpNr, self.name)

        return activeCounter + 1

    def doMyRolloDown(self, inOut, currentTime, activeCounter):

        #Terra Rechts wieder besonders
        if self.rollStatus == self.ROLLSTATUS_TERRA_RIGHT_SHOULD_TRY:
            self.stopTime = currentTime + timedelta(milliseconds=2500)
            self.rollStatus = self.ROLLSTATUS_TERRA_RIGHT_TRY
        else:
            self.stopTime = currentTime + timedelta(milliseconds=self.rollDuration)
            self.rollStatus = self.ROLLSTATUS_ONE_DOWN

        inOut.doRolloDown(self.mcpNr, self.name)

        return activeCounter + 1

    def doMyRolloStop(self, inOut, activeCounter):
        if self.upWithClock:
            self.shouldUpToday = False
            self.upWithClock = False

        if self.downWithClock:
            self.shouldDownToday = False
            self.downWithClock = False

        self.rollStatus = self.ROLLSTATUS_IDLE
        self.stopTime = db.TIME_FOR_COMP
        inOut.doRolloStop(self.mcpNr, self.name)

        return activeCounter - 1

    def doMyRolloClearCommand(self):
        self.rollStatus = self.ROLLSTATUS_IDLE
        self.stopTime = db.TIME_FOR_COMP


