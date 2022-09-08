from datetime import datetime
from queue import Queue

import logging
import csv

from sunTimeHandler import SunTimeHandler
from alarm import Alarm
from room import Room
from pump import Pump
from fan import Fan
from radio import Radio
from houseTime import HouseTime
from inputOutput import InputOutput as iO


def init():

    #ist quasi die 0, für Vergleiche
    global TIME_FOR_COMP
    TIME_FOR_COMP = datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)

    global STOP_THREAD
    STOP_THREAD = "StopThread"

    global pump
    pump = Pump()
    pump.writeTextFileToPumpTime()

    global fan
    fan = Fan()

    global radio
    radio = Radio()

    global alarm
    alarm = Alarm()

    global houseTime
    houseTime = HouseTime()
    houseTime.writeTextFileToHouseTime()

    global sunTime
    sunTime = SunTimeHandler()
    sunTime.setSuntime()

    global myQueue
    myQueue = Queue()

    #-----Zimmer Initialisern-----
    terraLeft = Room(Room.TERRA_LEFT, iO.BIT_UP_TERRA_LEFT_1, iO.BIT_DOWN_TERRA_LEFT_1, Room.MCP1, Room.ROLLO_RUNTIME_LONG, Room.UP_TERRA_LEFT, Room.DOWN_TERRA_LEFT )
    terraRight = Room(Room.TERRA_RIGHT, iO.BIT_UP_TERRA_RIGHT_1, iO.BIT_DOWN_TERRA_RIGHT_1, Room.MCP1, Room.ROLLO_RUNTIME_LONG, Room.UP_TERRA_RIGHT, Room.DOWN_TERRA_RIGHT)
    livingGarage = Room(Room.LIVING_GARAGE, iO.BIT_UP_LIVING_GARAGE_1, iO.BIT_DOWN_LIVING_GARAGE_1, Room.MCP1, Room.ROLLO_RUNTIME_LONG, Room.UP_LIVING_GARAGE, Room.DOWN_LIVING_GARAGE)
    kitchen = Room(Room.KITCHEN, iO.BIT_UP_KITCHEN_1, iO.BIT_DOWN_KITCHEN_1, Room.MCP1, Room.ROLLO_RUNTIME_SHORT, Room.UP_KITCHEN, Room.DOWN_KITCHEN)
    guestToilet = Room(Room.GUEST_TOILET, iO.BIT_UP_GUEST_TOILET_1, iO.BIT_DOWN_GUEST_TOILET_1, Room.MCP1, Room.ROLLO_RUNTIME_SHORT, Room.UP_GUEST_TOILET, Room.DOWN_GUEST_TOILET)

    leaSleep = Room(Room.LEA_SLEEP, iO.BIT_UP_LEA_SLEEPING_2, iO.BIT_DOWN_LEA_SLEEPING_2, Room.MCP2, Room.ROLLO_RUNTIME_SHORT, Room.UP_LEA_SLEEP, Room.DOWN_LEA_SLEEP)
    leaLiving = Room(Room.LEA_LIVING, iO.BIT_UP_LEA_LIVING_2, iO.BIT_DOWN_LEA_LIVING_2, Room.MCP2, Room.ROLLO_RUNTIME_SHORT, Room.UP_LEA_LIVING, Room.DOWN_LEA_LIVNG)
    parents = Room(Room.PARENTS, iO.BIT_UP_PARENTS_2, iO.BIT_DOWN_PARENTS_2, Room.MCP2, Room.ROLLO_RUNTIME_SHORT, Room.UP_PARENTS, Room.DOWN_PARENTS)
    toilet = Room(Room.TOILET, iO.BIT_UP_TOILET_2, iO.BIT_DOWN_TOILET_2, Room.MCP2, Room.ROLLO_RUNTIME_SHORT, Room.UP_TOILET, Room.DOWN_TOILET)
    jan = Room(Room.JAN, iO.BIT_UP_JAN_2, iO.BIT_DOWN_JAN_2, Room.MCP2, Room.ROLLO_RUNTIME_SHORT, Room.UP_JAN, Room.DOWN_JAN)

    #Reihenfolge im Dict gibt an, in welcher Reihenfolge die Rolladen gefahren werden
    global house
    house = {Room.TERRA_RIGHT:terraRight, Room.LIVING_GARAGE :livingGarage, Room.GUEST_TOILET:guestToilet,
             Room.TERRA_LEFT:terraLeft, Room.KITCHEN:kitchen,  Room.PARENTS:parents,
             Room.LEA_SLEEP:leaSleep, Room.LEA_LIVING:leaLiving, Room.TOILET:toilet,
            Room.JAN:jan}


    #Evtl werden die Rolladenzeiten einzeln gespeichert
    try:
        with open("roomTimes.csv", "r") as file:
            reader = csv.reader(file)
            next(reader, None)
            #row = ["name", "upTime", "upTimeWebSite", "gotOwnUpTime", "allowUpToday", "downTime", "downTimeWebSite", "gotOwnDownTime", "allowDownToday"])
            for row in reader:
                house[row[0]].upTime = row[1]
                house[row[0]].upTimeWebSite = row[2]
                house[row[0]].gotOwnUpTime = row[3]
                house[row[0]].allowUpToday = row[4]
                house[row[0]].downTime = row[5]
                house[row[0]].downTimeWebSite = row[6]
                house[row[0]].gotOwnDownTime = row[7]
                house[row[0]].allowDownToday = row[8]

                logging.info("    -Name: {} UpTime: {} UpTimeWebSite: {} gotOwnUpTime: {} allowUpToday: {} downTime: {} downTimeWebSite: {} gotOwnDownTime: {} allowDownToday: {}"
                    .format(house[row[0]].name,
                        house[row[0]].upTime, house[row[0]].upTimeWebSite, house[row[0]].gotOwnUpTime, house[row[0]].allowUpToday, 
                        house[row[0]].downTime, house[row[0]].downTimeWebSite, house[row[0]].gotOwnDownTime, house[row[0]].allowDownToday))

    except BaseException as e:
        logging.error("     - Error Load individual room times")
        logging.error(str(e))