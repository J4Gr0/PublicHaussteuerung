from datetime import datetime, timedelta
from random import randint
from time import sleep

import logging

import dataBase as db
from inputOutput import InputOutput


class HouseController:

    def __init__(self):
        self.inOut = InputOutput()

        self.currentTime = datetime.now()
        self.previousTime = self.currentTime
        self.previousDay = self.currentTime

        self.todoItem = None

#-----Rollo
        self.someRolloIsPerforming = False
        self.rollIndex = 0
        self.countOfActiveRollo = 0

        self.timeStampForOpenGroundCentral = db.TIME_FOR_COMP

#-----UP Button
        self.upButtonPressTimeStamp = db.TIME_FOR_COMP
        self.upButtonPressTimeDuration = timedelta(milliseconds=0)
        self.upButtonStopTime = db.TIME_FOR_COMP

#-----Down Button
        self.downButtonPressTimeStamp = db.TIME_FOR_COMP
        self.downButtonPressTimeDuration = timedelta(milliseconds=0)
        self.downButtonStopTime = db.TIME_FOR_COMP

        #initial alle Räume setzten auf eine Zeit
        self.randNum = randint(-db.Room.RANDOM_RANGE, db.Room.RANDOM_RANGE)
        for key, room in db.house.items():
            if room.gotOwnUpTime == "checked":
                room.setUpTimeParameters(room.upTimeWebSite, True, room.gotOwnUpTime, room.allowUpToday)
            else:
                if self.__castStringTimeToDateTime(self.currentTime, db.houseTime.getTodayUpTime(self.currentTime)) > self.__castStringTimeToDateTime(self.currentTime, db.sunTime.getTodaySunRise(self.currentTime)) + timedelta(minutes = db.houseTime.offSetMorning):
                    room.setUpTimeParameters(db.houseTime.getTodayUpTime(self.currentTime), False, room.gotOwnUpTime, room.allowUpToday, self.randNum)
                else:
                    upTime = self.currentTime.replace(hour=int(db.sunTime.getTodaySunRise(self.currentTime)[0:2]), minute=int( db.sunTime.getTodaySunRise(self.currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetMorning)
                    upTimeStr = upTime.strftime("%H:%M")
                    room.setUpTimeParameters(upTimeStr, False ,room.gotOwnUpTime, room.allowUpToday, self.randNum)

            if room.gotOwnDownTime == "checked":
                room.setDownTimeParameters(room.downTimeWebSite,True, room.gotOwnDownTime, room.allowDownToday)
            else:
                if self.__castStringTimeToDateTime(self.currentTime, db.houseTime.getTodayDownTime(self.currentTime)) < self.__castStringTimeToDateTime(self.currentTime, db.sunTime.getTodaySunSet(self.currentTime)) + timedelta(minutes = db.houseTime.offSetEvening):
                    room.setDownTimeParameters(db.houseTime.getTodayDownTime(self.currentTime), False, room.gotOwnDownTime, room.allowDownToday, self.randNum)
                else:
                    downTime = self.currentTime.replace(hour=int(db.sunTime.getTodaySunSet(self.currentTime)[0:2]), minute=int( db.sunTime.getTodaySunSet(self.currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetEvening)
                    downTimeStr = downTime.strftime("%H:%M")
                    room.setDownTimeParameters(downTimeStr, False, room.gotOwnDownTime, room.allowDownToday, self.randNum)

    def houseControlling(self):
        while(True):
            #Zeit die die while True schleifen schlafen soll :D
            sleep(0.01)

            #self.currentTime für die nächste Iteration
            self.currentTime = datetime.now()

            #Led blinken lassen
            if (self.currentTime - self.previousTime) > timedelta(seconds=1):
                self.inOut.toggleActiveLED()
                self.previousTime = self.currentTime

            #Day Changed
            if self.currentTime.weekday() != self.previousDay.weekday():
                logging.info("     - Day changed")
                self.previousDay = self.currentTime

                #Sonnenzeit nochmal neu berechnen
                db.sunTime.setSuntime()

                #wenn der Tag gewechselt wurde, setzt für den neuen Tag die hoch und runter Parameter
                self.randNum = randint(-db.Room.RANDOM_RANGE, db.Room.RANDOM_RANGE)
                for key, room in db.house.items():
                    if room.gotOwnUpTime == "checked":
                        room.setUpTimeParameters(room.upTimeWebSite, True, room.gotOwnUpTime, room.allowUpToday)
                    else:
                        if self.__castStringTimeToDateTime(self.currentTime, db.houseTime.getTodayUpTime(self.currentTime)) > self.__castStringTimeToDateTime(self.currentTime, db.sunTime.getTodaySunRise(self.currentTime)) + timedelta(minutes = db.houseTime.offSetMorning):
                            room.setUpTimeParameters(db.houseTime.getTodayUpTime(self.currentTime), False, room.gotOwnUpTime, room.allowUpToday, self.randNum)
                        else:
                            upTime = self.currentTime.replace(hour=int(db.sunTime.getTodaySunRise(self.currentTime)[0:2]), minute=int( db.sunTime.getTodaySunRise(self.currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetMorning)
                            upTimeStr = upTime.strftime("%H:%M")
                            room.setUpTimeParameters(upTimeStr, False ,room.gotOwnUpTime, room.allowUpToday, self.randNum)

                    if room.gotOwnDownTime == "checked":
                        room.setDownTimeParameters(room.downTimeWebSite,True, room.gotOwnDownTime, room.allowDownToday)
                    else:
                        if self.__castStringTimeToDateTime(self.currentTime, db.houseTime.getTodayDownTime(self.currentTime)) < self.__castStringTimeToDateTime(self.currentTime, db.sunTime.getTodaySunSet(self.currentTime)) + timedelta(minutes = db.houseTime.offSetEvening):
                            room.setDownTimeParameters(db.houseTime.getTodayDownTime(self.currentTime), False, room.gotOwnDownTime, room.allowDownToday, self.randNum)
                        else:
                            downTime = self.currentTime.replace(hour=int(db.sunTime.getTodaySunSet(self.currentTime)[0:2]), minute=int( db.sunTime.getTodaySunSet(self.currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetEvening)
                            downTimeStr = downTime.strftime("%H:%M")
                            room.setDownTimeParameters(downTimeStr, False, room.gotOwnDownTime, room.allowDownToday, self.randNum)


            #Check if Alarm can start, right before it may get activated
            if not db.alarm.alarmIsOn:
                db.alarm.checkAlarmCanStart(self.inOut)

#------Handle Queue Items
            if not db.myQueue.empty():
                #Aktuelles Item aus der Queue holen für die nächste Iteration
                self.todoItem = db.myQueue.get_nowait()

                if self.todoItem == db.Alarm.START_ALARM:
                    if db.alarm.alarmCanStart:
                        db.alarm.startAlarm()
                        continue

                elif self.todoItem == db.Alarm.STOP_ALARM:
                    db.alarm.stopAlarm(self.inOut, self.currentTime)
                    continue

                elif self.todoItem == db.Fan.START_FAN_SHORT:
                    if not db.fan.fanIsOn:
                        db.fan.startFan(self.inOut, self.currentTime, db.Fan.FAN_RUNTIME_SHORT)
                        continue

                elif self.todoItem == db.Fan.START_FAN_LONG:
                    if not db.fan.fanIsOn:
                        db.fan.startFan(self.inOut, self.currentTime, db.Fan.FAN_RUNTIME_LONG)
                        continue

                elif self.todoItem == db.Fan.STOP_FAN:
                    if db.fan.fanIsOn:
                        db.fan.stopFan(self.inOut)
                        continue

                elif self.todoItem == db.Radio.START_RADIO_SHORT:
                    if not db.radio.radioIsOn:
                        db.radio.startRadio(self.inOut, self.currentTime, db.Radio.RADIO_RUNTIME_SHORT)
                        continue

                elif self.todoItem == db.Radio.START_RADIO_LONG:
                    if not db.radio.radioIsOn:
                        db.radio.startRadio(self.inOut, self.currentTime, db.Radio.RADIO_RUNTIME_LONG)
                        continue

                elif self.todoItem == db.Radio.STOP_RADIO:
                    if db.radio.radioIsOn:
                        db.radio.stopRadio(self.inOut)
                        continue

                elif self.todoItem == db.Pump.START_PUMP:
                    if not db.pump.pumpIsOn:
                        db.pump.startPump(self.inOut, self.currentTime)
                        continue

                elif self.todoItem == db.Pump.STOP_PUMP:
                    if db.pump.pumpIsOn:
                        db.pump.stopPump(self.inOut)
                        continue

                elif self.todoItem == db.Room.UP_ALL:
                    if self.someRolloIsPerforming:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doAllRoomsStatusUp()
                        continue

                elif self.todoItem == db.Room.DOWN_ALL:
                    if self.someRolloIsPerforming:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doAllRoomsStatusDown()
                        continue

                elif self.todoItem == db.STOP_THREAD:
                    break

                else:
                    for key, room in db.house.items():

                        if self.todoItem == room.upItemQueue:
                            #unterscheide, welchen Rollstatus das aktuelle Zimmer hat und setze den entsprechenden Rollstatus
                            if room.rollStatus == db.Room.ROLLSTATUS_ONE_DOWN:
                                logging.info("   -   STOP {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_STOP

                            elif room.rollStatus == db.Room.ROLLSTATUS_ONE_SHOULD_DOWN:
                                logging.info("    -  Clear Down {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_CLEAR_COMMAND

                            else:
                                logging.info("   -   UP {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP
                                self.someRolloIsPerforming = True

                        elif self.todoItem == room.downItemQueue:
                            #is this Rollo on right now
                            if room.rollStatus == db.Room.ROLLSTATUS_ONE_UP:
                                logging.info("   -   STOP {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_STOP
                            
                            elif room.rollStatus == db.Room.ROLLSTATUS_ONE_SHOULD_UP:
                                logging.info("    -  Clear Up {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_CLEAR_COMMAND

                            else:
                                logging.info("   -   DOWN {} Website".format(room.name))
                                room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN
                                self.someRolloIsPerforming = True
                    continue

                self.todoItem = None

#-----Alarm
            if db.alarm.alarmIsOn:
                if self.currentTime > db.alarm.alarmStopTime and db.alarm.alarmSignalAlreadyTriggerd:
                    db.alarm.stopAlarmSignal(self.inOut, self.currentTime)
                else:
                    if db.alarm.isOneWindowOpen(self.inOut) and not db.alarm.alarmSignalAlreadyTriggerd:
                        db.alarm.triggerAlarmSignal(self.inOut, self.currentTime)


#-----Rollo Zeit Logik
            for key, room in db.house.items():
                #Überprüfe, ob die Rollade des Zimmers Hoch oder runterfahren soll. Gegenbenfalls stoppen und in die andere Richtung fahren
                if room.shouldUpToday:
                    if room.castStringTimeToDateTime(self.currentTime, room.upTime) < self.currentTime:
                        #is driving down ? -> stop and go Up
                        if room.rollStatus == db.Room.ROLLSTATUS_ONE_DOWN:
                            self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)
                            sleep(0.01)
                            self.someRolloIsPerforming = True
                            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP
                        #is idle -> start
                        elif room.rollStatus == db.Room.ROLLSTATUS_IDLE:
                            self.someRolloIsPerforming = True
                            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP
                            room.upWithClock = True
                
                if room.shouldDownToday:
                    if room.castStringTimeToDateTime(self.currentTime, room.downTime) < self.currentTime:
                        #is driving up ? -> stop and go Down
                        if room.rollStatus == db.Room.ROLLSTATUS_ONE_UP:
                            self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)
                            sleep(0.01)
                            self.someRolloIsPerforming = True
                            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN
                        #is idle -> start
                        elif room.rollStatus == db.Room.ROLLSTATUS_IDLE:
                            #Überprüfe, ob das Fenster der Rollade bei Terra Rechts offen ist
                            if room.name == db.Room.TERRA_RIGHT:
                                if self.inOut.isTerraRightWindowOpen():
                                    room.shouldDownToday = False
                                else:
                                    room.rollStatus = db.Room.ROLLSTATUS_TERRA_RIGHT_SHOULD_TRY
                            else:
                                room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN 

                            self.someRolloIsPerforming = True
                            room.downWithClock = True

#-----Rollo Logic

            #Für das Terassenfenster rechts überprüfen, ob es geöffnet wurde und dann etweder hoch oder runterfahren
            if db.house[db.Room.TERRA_RIGHT].rollStatus == db.Room.ROLLSTATUS_TERRA_COMPLETE:   
                if self.someRolloIsPerforming:
                    if self.inOut.isTerraRightWindowOpen():
                        db.house[db.Room.TERRA_RIGHT].rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP
                else:       
                    db.house[db.Room.TERRA_RIGHT].rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN
                    self.someRolloIsPerforming = True                    


            if self.inOut.isRolloLEDActive() and not self.someRolloIsPerforming:
                self.inOut.deactivateRolloLED()

            #Wenn irgendeine Rolladen fährt, Rollo Logik
            if self.someRolloIsPerforming:
                if not self.inOut.isRolloLEDActive():
                    self.inOut.activateRolloLED()
                #für jedes Zimmer im Haus überprüfe die verschiedenen Rollstati und handle entsprechend
                for key, room in db.house.items():
                    
                    #Rollo stoppen
                    if room.rollStatus == db.Room.ROLLSTATUS_ONE_UP or room.rollStatus == db.Room.ROLLSTATUS_ONE_DOWN:
                        if self.currentTime > room.stopTime:
                            self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)

                    if room.rollStatus != db.Room.ROLLSTATUS_IDLE and self.countOfActiveRollo < 3:
                        if room.rollStatus == db.Room.ROLLSTATUS_ONE_SHOULD_UP:
                            self.countOfActiveRollo = room.doMyRolloUp(self.inOut, self.currentTime, self.countOfActiveRollo)

                        if room.rollStatus == db.Room.ROLLSTATUS_ONE_SHOULD_DOWN:
                            self.countOfActiveRollo = room.doMyRolloDown(self.inOut, self.currentTime, self.countOfActiveRollo)

                        if room.rollStatus == db.Room.ROLLSTATUS_TERRA_RIGHT_SHOULD_TRY:
                            self.countOfActiveRollo = room.doMyRolloDown(self.inOut, self.currentTime, self.countOfActiveRollo)

                    #Rollade Terrasse Rechts wieder seperat überprüfen
                    if room.rollStatus == db.Room.ROLLSTATUS_TERRA_RIGHT_TRY:
                        #after 3Sek stop it
                        if self.currentTime > room.stopTime:
                            self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)
                            room.rollStatus = db.Room.ROLLSTATUS_TERRA_COMPLETE
                        #if Door was open, stop and go Up
                        if self.inOut.isTerraRightWindowOpen():
                            self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)
                            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP

                    if room.rollStatus == db.Room.ROLLSTATUS_STOP:
                        self.countOfActiveRollo = room.doMyRolloStop(self.inOut, self.countOfActiveRollo)

                    if room.rollStatus == db.Room.ROLLSTATUS_CLEAR_COMMAND:
                        room.doMyRolloClearCommand()

                #wenn kein Rollo fährt
                if self.countOfActiveRollo == 0:
                    self.someRolloIsPerforming = False
            else:
                #Wenn keine Rollo mehr fährt, setze noch eine Zeit, sodass eine Sekunde später erst Ground Central wieder freigegeben wird
                if self.inOut.isGroundCentralOn():
                    if self.timeStampForOpenGroundCentral == db.TIME_FOR_COMP:
                        self.timeStampForOpenGroundCentral = self.currentTime + timedelta(milliseconds=1000)
                        logging.info("   -   Ground Central Stop Time: {} ".format(self.timeStampForOpenGroundCentral))
                    else:
                        if self.timeStampForOpenGroundCentral < self.currentTime and self.timeStampForOpenGroundCentral != db.TIME_FOR_COMP:
                            self.timeStampForOpenGroundCentral = db.TIME_FOR_COMP
                            self.inOut.deactivateGroundCentral()

#-----Rollo Up Button

            #Saving time when upButton is pressed
            if self.inOut.isUpButtonPressed() and self.upButtonPressTimeStamp == db.TIME_FOR_COMP:
                logging.info("   -   UP Button pressed")
                self.upButtonPressTimeStamp = self.currentTime

            #for indicating extra Up Cycle
            if self.upButtonPressTimeStamp > db.TIME_FOR_COMP and self.inOut.isUpButtonPressed():
                self.upPressTimeDuration = self.currentTime - self.upButtonPressTimeStamp
                if self.upPressTimeDuration > timedelta(milliseconds=2000):
                    self.inOut.activateRolloLED()

            #upButton was pressed and int pressed right now
            if self.upButtonPressTimeStamp > db.TIME_FOR_COMP and not self.inOut.isUpButtonPressed():
                self.inOut.deactivateRolloLED()
                self.upButtonPressTimeDuration = self.currentTime - self.upButtonPressTimeStamp
                self.upButtonPressTimeStamp = db.TIME_FOR_COMP
                logging.info("   -   UP Button pressed for {} ".format(self.upButtonPressTimeDuration.seconds))

                if self.upButtonPressTimeDuration > timedelta(milliseconds=2000):
                    if self.someRolloIsPerforming == True:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doSomeRoomsStatusUp()
                        continue

                if self.upButtonPressTimeDuration > timedelta(milliseconds=100):
                    if self.someRolloIsPerforming == True:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doAllRoomsStatusUp()
                        continue

#-----Rollo Down Button

            #Saving time when downButton is pressed
            if self.inOut.isDownButtonPressed() and self.downButtonPressTimeStamp == db.TIME_FOR_COMP:
                logging.info("   -   DOWN Button pressed")
                self.downButtonPressTimeStamp = self.currentTime

            #for indicating extra Down Cycle
            if self.downButtonPressTimeStamp > db.TIME_FOR_COMP and self.inOut.isDownButtonPressed():
                self.downPressTimeDuration = self.currentTime - self.downButtonPressTimeStamp
                if self.downPressTimeDuration > timedelta(milliseconds=2000):
                    self.inOut.activateRolloLED()

            #upButton was pressed and int pressed right now
            if self.downButtonPressTimeStamp > db.TIME_FOR_COMP and not self.inOut.isDownButtonPressed():
                self.inOut.deactivateRolloLED()
                self.downButtonPressTimeDuration = self.currentTime - self.downButtonPressTimeStamp
                self.downButtonPressTimeStamp = db.TIME_FOR_COMP
                logging.info("   -   DOWN Button pressed for {} ".format(self.downButtonPressTimeDuration.seconds))

                if self.downButtonPressTimeDuration > timedelta(milliseconds=2000):
                    if self.someRolloIsPerforming == True:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doSomeRoomsStatusDown()
                        continue

                if self.downButtonPressTimeDuration > timedelta(milliseconds=100):
                    if self.someRolloIsPerforming == True:
                        self.__doAllRoomsStatusIdleAndStop()
                        continue
                    else:
                        self.__doAllRoomsStatusDown()
                        continue

#-----Fan and Radio Handling Handling

            #Saving time when fanButton is pressed
            #When fan pressed 
            if self.inOut.isFanButtonPressed() and db.fan.fanPressTimeStamp == db.TIME_FOR_COMP:
                logging.info("   -   FAN Button pressed")
                db.fan.fanPressTimeStamp = self.currentTime

            #For Indicating when you can activate Fan or Radio
            if db.fan.fanPressTimeStamp > db.TIME_FOR_COMP and self.inOut.isFanButtonPressed():   
                db.fan.fanPressTimeDuration = self.currentTime - db.fan.fanPressTimeStamp
                if db.fan.fanPressTimeDuration <= timedelta(milliseconds=db.radio.RADIO_PRESS_INTERVALL) and\
                                db.fan.fanPressTimeDuration >= timedelta(milliseconds=db.fan.FAN_PRESS_INTERVALL):
                    self.inOut.activatePumpLED()

                if db.fan.fanPressTimeDuration >= timedelta(milliseconds = db.radio.RADIO_PRESS_INTERVALL):
                    self.inOut.deactivatePumpLED()


            #If fanButton was pressed and isnt pressed right now
            if db.fan.fanPressTimeStamp > db.TIME_FOR_COMP and not self.inOut.isFanButtonPressed():
                self.inOut.deactivatePumpLED()
                #How long was the fanButton pressed
                db.fan.fanPressTimeDuration = self.currentTime - db.fan.fanPressTimeStamp
                db.fan.fanPressTimeStamp = db.TIME_FOR_COMP
                logging.info("   -   FAN Button pressed {}".format(db.fan.fanPressTimeDuration.seconds))

                #fanPressTime between Fan and Radio Intervall -> activate Fan
                if db.fan.fanPressTimeDuration <= timedelta(milliseconds=int(db.radio.RADIO_PRESS_INTERVALL)) and \
                 db.fan.fanPressTimeDuration >= timedelta(milliseconds=int(db.fan.FAN_PRESS_INTERVALL)):

                    #If Fan not started yet -> activate and saving StopTime
                    if db.fan.fanStopTime == db.TIME_FOR_COMP and db.fan.fanIsOn == False:
                        db.fan.startFan(self.inOut, self.currentTime, db.Fan.FAN_RUNTIME_LONG)
                        continue
                    
                    #If Fan is started and fanButton pressed again and NEXT Iteration -> Stop Fan
                    if db.fan.fanStopTime > db.TIME_FOR_COMP and db.fan.fanIsOn:
                        db.fan.stopFan(self.inOut)
                        logging.info("   -   FAN Stopped, Button Pressed")
                        continue

                #fanPressTime is bigger than Radio and Fanintervall -> activate Radio
                if db.fan.fanPressTimeDuration >= timedelta(milliseconds = db.radio.RADIO_PRESS_INTERVALL):

                    #If Radio not started yet -> activate and saving StopTime
                    if db.radio.radioStopTime == db.TIME_FOR_COMP and db.radio.radioIsOn == False:
                        db.fan.fanPressTimeDuration = db.TIME_FOR_COMP
                        db.radio.startRadio(self.inOut, self.currentTime, db.Radio.RADIO_RUNTIME_LONG)
                        continue

                    #If Radio is started fanButton pressed again and NEXT Iteration -> Stop Radio
                    if db.radio.radioStopTime > db.TIME_FOR_COMP and db.radio.radioIsOn:
                        db.fan.fanPressTimeDuration = db.TIME_FOR_COMP
                        db.radio.stopRadio(self.inOut)
                        logging.info("   -   RADIO Stopped, Button Pressed")
                        continue

            if self.currentTime >= db.fan.fanStopTime and db.fan.fanIsOn:
                db.fan.stopFan(self.inOut)
                logging.info("   -   FAN Stopped, TIME OUT")

            if self.currentTime >= db.radio.radioStopTime and db.radio.radioIsOn:
                db.radio.stopRadio(self.inOut)
                logging.info("   -   RADIO Stopped, TIME OUT")

#-----Pump Handling
            #Saving time when pumpButton is pressed
            if self.inOut.isPumpButtonPressed() and db.pump.pumpPressTimeStamp == db.TIME_FOR_COMP:
                logging.info("   -   PUMP Button Pressed")
                db.pump.pumpPressTimeStamp = self.currentTime

            #if pumpButton was pressed and isnt pressed right now
            if db.pump.pumpPressTimeStamp > db.TIME_FOR_COMP and not self.inOut.isPumpButtonPressed():
                db.pump.pumpPressTimeStamp = db.TIME_FOR_COMP

                if db.house[db.Room.TERRA_RIGHT].rollStatus == db.Room.ROLLSTATUS_TERRA_COMPLETE or db.house[db.Room.TERRA_RIGHT].rollStatus == db.Room.ROLLSTATUS_TERRA_RIGHT_TRY:            
                    if self.someRolloIsPerforming:
                        db.house[db.Room.TERRA_RIGHT].rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP
                        continue

                if db.pump.pumpIsOn == False:
                    db.pump.startPump(self.inOut, self.currentTime)
                else:
                    db.pump.stopPump(self.inOut)
                    logging.info("   -   PUMP Stopped, Button Pressed")

            if self.currentTime >= db.pump.pumpStopTime and db.pump.pumpIsOn:
                db.pump.stopPump(self.inOut)
                db.pump.lastTimeRunned = self.currentTime
                logging.info("   -   PUMP Stopped, Time Out")


            #PumpTime Changed from Website, Update and check if run today 
            if db.pump.pumpTime[str(self.currentTime.weekday())][2] == db.pump.NEED_TO_UPDATE:
                logging.info("     -Pump Time Update in Loop")
                db.pump.pumpShouldRunToday = db.pump.getTodayPumpTime(self.currentTime) > self.currentTime
                db.pump.pumpTime[str(self.currentTime.weekday())][2]  = db.pump.UP_TO_DATE

            if db.pump.pumpTime[str(self.currentTime.weekday())][1]  == "checked" and db.pump.pumpShouldRunToday == True:
                tempPumpTime = db.pump.getTodayPumpTime(self.currentTime)
                if tempPumpTime.hour ==  self.currentTime.hour and tempPumpTime.minute == self.currentTime.minute:
                    logging.info("     -Pump started with Time")
                    db.pump.pumpShouldRunToday = False
                    db.pump.startPump(self.inOut, self.currentTime)


        self.inOut.cleanUp()
        logging.info("     - MainLoop Verlassen")


#-----Private Functions
    def __castStringTimeToDateTime(self, currentTime, stringTime):
        return currentTime.replace(hour=int(stringTime[0:2]), minute=int(stringTime[3:5]), second=0)

    def __doAllRoomsStatusIdleAndStop(self):
        logging.info("   -   IDLE STATUS ALL ROOMS")
        self.someRolloIsPerforming = False
        self.countOfActiveRollo = 0
        for key, room in db.house.items():
            room.rollStatus = db.Room.ROLLSTATUS_IDLE
            room.stopTime = db.TIME_FOR_COMP
        self.inOut.stopAllRollo()

    def __doAllRoomsStatusUp(self):
        logging.info("   -   UP STATUS ALL ROOMS")
        self.someRolloIsPerforming = True
        for key, room in db.house.items():
            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP

    def __doSomeRoomsStatusUp(self):
        logging.info("   -   UP STATUS SOME ROOMS")
        self.someRolloIsPerforming = True
        for key, room in db.house.items():
            if room.name == db.Room.JAN or room.name == db.Room.LEA_SLEEP or room.name == db.Room.PARENTS:
                continue
            else:
                room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_UP

    def __doAllRoomsStatusDown(self):
        logging.info("   -   DOWN STATUS ALL ROOMS")
        self.someRolloIsPerforming = True
        for key, room in db.house.items():
            room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN


    def __doSomeRoomsStatusDown(self):
        logging.info("   -   DOWN STATUS SOME ROOMS")
        self.someRolloIsPerforming = True
        for key, room in db.house.items():
            if not room.name == db.Room.TERRA_RIGHT:
                room.rollStatus = db.Room.ROLLSTATUS_ONE_SHOULD_DOWN









