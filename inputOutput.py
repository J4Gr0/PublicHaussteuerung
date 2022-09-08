from datetime import datetime
from time import sleep
from gpiozero import Button, LED
from portExpander import MCP23S17

import logging

import dataBase as db

class InputOutput:

    #-----Bits for Portexpander-----
    BIT_UP_TERRA_RIGHT_1 = 3
    BIT_DOWN_TERRA_RIGHT_1 = 4

    BIT_UP_TERRA_LEFT_1 = 5
    BIT_DOWN_TERRA_LEFT_1 = 6

    BIT_UP_LIVING_GARAGE_1 = 7
    BIT_DOWN_LIVING_GARAGE_1 = 8

    BIT_UP_GUEST_TOILET_1 = 11
    BIT_DOWN_GUEST_TOILET_1 = 12

    BIT_UP_KITCHEN_1 = 9
    BIT_DOWN_KITCHEN_1 = 10


    BIT_UP_LEA_LIVING_2 = 5
    BIT_DOWN_LEA_LIVING_2 = 6

    BIT_UP_LEA_SLEEPING_2 = 3
    BIT_DOWN_LEA_SLEEPING_2 = 4

    BIT_UP_PARENTS_2 = 7
    BIT_DOWN_PARENTS_2 = 8

    BIT_UP_TOILET_2 = 9
    BIT_DOWN_TOILET_2 = 10

    BIT_UP_JAN_2 = 11
    BIT_DOWN_JAN_2 = 12

    def __init__(self):
#-----PINS FOR BUTTON OR LEDS

        self.__PIN_UP_BUTTON = 12
        self.__PIN_FAN_OUTPUT = 13
        self.__PIN_DOWN_BUTTON = 16
        self.__PIN_LED_ACTIVE = 17
        self.__PIN_GROUND_CENTRAL = 18
        self.__PIN_ALARM_OUTPUT = 19
        self.__PIN_PUMP_BUTTON  = 20
        self.__PIN_FAN_BUTTON = 21
        self.__PIN_ROLLO_LED = 22
        self.__PIN_PUMP_OUTPUT = 23
        self.__PIN_MAGNET_TERRA_RIGHT = 24
        self.__PIN_MAGNET_OTHERS = 25
        self.__PIN_RADIO_OUTPUT = 26
        self.__PIN_PUMP_LED = 27

#-----Initiliaze GPIO
        self.__pumpButton = Button(pin=self.__PIN_PUMP_BUTTON)
        self.__fanButton = Button(pin=self.__PIN_FAN_BUTTON)
        self.__upButton = Button(pin=self.__PIN_UP_BUTTON)
        self.__downButton = Button(pin=self.__PIN_DOWN_BUTTON)

        self.__magnetTerraRight = Button(pin=self.__PIN_MAGNET_TERRA_RIGHT)
        self.__magnetOthers = Button(pin=self.__PIN_MAGNET_OTHERS)

        self.__pumpLED = LED(pin=self.__PIN_PUMP_LED)
        self.__pumpLED.off()

        self.__pumpOutput = LED(pin=self.__PIN_PUMP_OUTPUT)
        self.__pumpOutput.off()

        self.__fanOutput = LED(pin=self.__PIN_FAN_OUTPUT)
        self.__fanOutput.off()

        self.__radioOutput = LED(pin=self.__PIN_RADIO_OUTPUT)
        self.__radioOutput.off()

        self.__rolloLED = LED(pin=self.__PIN_ROLLO_LED)
        self.__rolloLED.off()

        self.__groundCentral = LED(pin=self.__PIN_GROUND_CENTRAL)
        self.__groundCentral.off()

        self.__activeLED = LED(pin=self.__PIN_LED_ACTIVE)
        self.__activeLED.off()

        self.__alarmOutput = LED(pin=self.__PIN_ALARM_OUTPUT)
        self.__alarmOutput.off()

#-----Initiliaze PortExpander

        self.__mcp1 = MCP23S17(device_id=0)
        self.__mcp1.open()
        self.__mcp1.max_speed_hz = 8000000

        for x in range(0, 16):
            self.__mcp1.setDirection(x, MCP23S17.DIR_OUTPUT)
            self.__mcp1.digitalWrite(x, MCP23S17.LEVEL_LOW)

        self.__mcp2 = MCP23S17(device_id=4)
        self.__mcp2.open()
        self.__mcp2.max_speed_hz = 8000000
        for x in range(0, 16):
            self.__mcp2.setDirection(x, MCP23S17.DIR_OUTPUT)
            self.__mcp2.digitalWrite(x, MCP23S17.LEVEL_LOW)


#-----Rollo Functions

    def isGroundCentralOn(self):
        return self.__groundCentral.is_active

    def activateGroundCentral(self):
        logging.info("   -   GroundCentral started")
        self.__groundCentral.on()

    def deactivateGroundCentral(self):
        logging.info("   -   GroundCentral stopped")
        self.__groundCentral.off()

    def stopAllRollo(self):
        logging.info("   -   Stopped all Rollo")
        self.__mcp1.writeGPIO(0x00)
        self.__mcp2.writeGPIO(0x00)

        sleep(0.1)
        self.deactivateGroundCentral()

    def doRolloUp(self, mcpNumber, name):

        if not self.isGroundCentralOn():
            self.activateGroundCentral()
            sleep(0.1)
        
        logging.info("   -   UP {}".format( name))

        if mcpNumber == db.Room.MCP1:
            if name == db.Room.TERRA_RIGHT:
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_RIGHT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_RIGHT_1, MCP23S17.LEVEL_HIGH)

            elif name ==  db.Room.TERRA_LEFT:
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_LEFT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_LEFT_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LIVING_GARAGE:
                self.__mcp1.digitalWrite(self.BIT_DOWN_LIVING_GARAGE_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_UP_LIVING_GARAGE_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.KITCHEN:
                self.__mcp1.digitalWrite(self.BIT_DOWN_KITCHEN_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_UP_KITCHEN_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.GUEST_TOILET:
                self.__mcp1.digitalWrite(self.BIT_DOWN_GUEST_TOILET_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_UP_GUEST_TOILET_1, MCP23S17.LEVEL_HIGH)

        elif mcpNumber == db.Room.MCP2:
            if name == db.Room.TOILET:
                self.__mcp2.digitalWrite(self.BIT_DOWN_TOILET_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_UP_TOILET_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.JAN:
                self.__mcp2.digitalWrite(self.BIT_DOWN_JAN_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_UP_JAN_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LEA_LIVING:
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_LIVING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_LIVING_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LEA_SLEEP:
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_SLEEPING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_SLEEPING_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.PARENTS:
                self.__mcp2.digitalWrite(self.BIT_DOWN_PARENTS_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_UP_PARENTS_2, MCP23S17.LEVEL_HIGH)


    def doRolloDown(self, mcpNumber, name):

        if not self.isGroundCentralOn():
            self.activateGroundCentral()
            sleep(0.1)

        logging.info("   -   DOWN {}".format( name))

        if mcpNumber == db.Room.MCP1:
            if name == db.Room.TERRA_RIGHT:
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_RIGHT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_RIGHT_1, MCP23S17.LEVEL_HIGH)

            elif name ==  db.Room.TERRA_LEFT:
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_LEFT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_LEFT_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LIVING_GARAGE:
                self.__mcp1.digitalWrite(self.BIT_UP_LIVING_GARAGE_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_LIVING_GARAGE_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.KITCHEN:
                self.__mcp1.digitalWrite(self.BIT_UP_KITCHEN_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_KITCHEN_1, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.GUEST_TOILET:
                self.__mcp1.digitalWrite(self.BIT_UP_GUEST_TOILET_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_GUEST_TOILET_1, MCP23S17.LEVEL_HIGH)

        elif mcpNumber == db.Room.MCP2:
            if name == db.Room.TOILET:
                self.__mcp2.digitalWrite(self.BIT_UP_TOILET_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_TOILET_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.JAN:
                self.__mcp2.digitalWrite(self.BIT_UP_JAN_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_JAN_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LEA_LIVING:
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_LIVING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_LIVING_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.LEA_SLEEP:
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_SLEEPING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_SLEEPING_2, MCP23S17.LEVEL_HIGH)

            elif name == db.Room.PARENTS:
                self.__mcp2.digitalWrite(self.BIT_UP_PARENTS_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_PARENTS_2, MCP23S17.LEVEL_HIGH)


    def doRolloStop(self, mcpNumber, name):

        logging.info("   -   STOP {}".format( name))

        if mcpNumber == db.Room.MCP1:
            if name == db.Room.TERRA_RIGHT:
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_RIGHT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_RIGHT_1, MCP23S17.LEVEL_LOW)

            elif name ==  db.Room.TERRA_LEFT:
                self.__mcp1.digitalWrite(self.BIT_UP_TERRA_LEFT_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_TERRA_LEFT_1, MCP23S17.LEVEL_LOW)

            elif name == db.Room.LIVING_GARAGE:
                self.__mcp1.digitalWrite(self.BIT_UP_LIVING_GARAGE_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_LIVING_GARAGE_1, MCP23S17.LEVEL_LOW)

            elif name == db.Room.KITCHEN:
                self.__mcp1.digitalWrite(self.BIT_UP_KITCHEN_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_KITCHEN_1, MCP23S17.LEVEL_LOW)

            elif name == db.Room.GUEST_TOILET:
                self.__mcp1.digitalWrite(self.BIT_UP_GUEST_TOILET_1, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp1.digitalWrite(self.BIT_DOWN_GUEST_TOILET_1, MCP23S17.LEVEL_LOW)

        elif mcpNumber == db.Room.MCP2:
            if name == db.Room.TOILET:
                self.__mcp2.digitalWrite(self.BIT_UP_TOILET_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_TOILET_2, MCP23S17.LEVEL_LOW)

            elif name == db.Room.JAN:
                self.__mcp2.digitalWrite(self.BIT_UP_JAN_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_JAN_2, MCP23S17.LEVEL_LOW)

            elif name == db.Room.LEA_LIVING:
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_LIVING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_LIVING_2, MCP23S17.LEVEL_LOW)

            elif name == db.Room.LEA_SLEEP:
                self.__mcp2.digitalWrite(self.BIT_UP_LEA_SLEEPING_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_LEA_SLEEPING_2, MCP23S17.LEVEL_LOW)

            elif name == db.Room.PARENTS:
                self.__mcp2.digitalWrite(self.BIT_UP_PARENTS_2, MCP23S17.LEVEL_LOW)
                sleep(0.01)
                self.__mcp2.digitalWrite(self.BIT_DOWN_PARENTS_2, MCP23S17.LEVEL_LOW)


#-----Magnet Button

    def isTerraRightWindowOpen(self):
        return not self.__magnetTerraRight.is_pressed

    def isOtherWindowOpen(self):
        return not self.__magnetOthers.is_pressed

    def activateAlarmSignal(self):
        self.__alarmOutput.on()

    def deactivateAlarmSignal(self):
        self.__alarmOutput.off()

#-----METHODS for Button Pressed
    def isFanButtonPressed(self):
        return self.__fanButton.is_pressed

    def isPumpButtonPressed(self):
        return self.__pumpButton.is_pressed

    def isUpButtonPressed(self):
        return self.__upButton.is_pressed

    def isDownButtonPressed(self):
        return self.__downButton.is_pressed

#-----Blinking Functions
    def activatePumpLED(self):
        #maybe toggle if led already on?
        self.__pumpLED.on()

    def deactivatePumpLED(self):
        self.__pumpLED.off()

    def activateRolloLED(self):
        self.__rolloLED.on()

    def deactivateRolloLED(self):
        self.__rolloLED.off()

    def isRolloLEDActive(self):
        return self.__rolloLED.is_active

    def activateActiveLED(self):
        self.__activeLED.on()

    def deactivateActiveLED(self):
        self.__activeLED.off()

    def toggleActiveLED(self):
        self.__activeLED.toggle()

    def showPumpNotRunAgain(self):
        self.__pumpLED.blink(on_time=0.5, off_time=0.5, n=3, background=True)


#-----Start and Stop Pump and Radio
    def activatePump(self):
        self.activatePumpLED()
        self.__pumpOutput.on()

    def deactivatePump(self):
        self.deactivatePumpLED()
        self.__pumpOutput.off()

    def activateRadio(self):
        self.__radioOutput.on()

    def deactivateRadio(self):
        self.__radioOutput.off()

    def activateFan(self):
        self.__fanOutput.on()

    def deactivateFan(self):
        self.__fanOutput.off()

#-----CleanUp Function
    def cleanUp(self):
        self.__pumpButton.close()
        self.__fanButton.close()
        self.__upButton.close()
        self.__downButton.close()
        self.__magnetOthers.close()
        self.__magnetTerraRight.close()

        self.__pumpLED.close()
        self.__pumpOutput.close()
        self.__fanOutput.close()
        self.__radioOutput.close()
        self.__rolloLED.close()
        self.__groundCentral.close()
        self.__activeLED.close()

        self.__mcp1.writeGPIO(0x00)
        self.__mcp1.close()
        self.__mcp2.writeGPIO(0x00)
        self.__mcp2.close()
