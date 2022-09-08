from datetime import datetime, time, timedelta
from random import randint
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from threading import Thread
from time import sleep
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter

import logging
import csv

import dataBase as db
from houseController import HouseController


app = Flask(__name__)
socketio = SocketIO(app)



#-----File Darstellung
@app.route("/log")
def showLog():
    logging.info("   -GET Logs User: {}".format(str(request.remote_addr)))
    try:
        with open("logs.log", "r") as f:
            logs = f.read()
        return render_template("log.html", content = logs)
    except Exception as e:
        logging.error(e)

@app.route("/pumptimecsv")
def showPumpTimeCSV():
    try:
        with open("pumpTime.csv", "r") as f:
            pumpTimeCSV = f.read()
        return render_template("pumpTimeCSV.html", content = pumpTimeCSV)
    except Exception as e:
        logging.error(e)

@app.route("/housetimecsv")
def showHouseTimeCSV():
    try:
        with open("houseTime.csv", "r") as f:
            houseTimeCSV = f.read()
        return render_template("houseTimeCSV.html", content = houseTimeCSV)
    except Exception as e:
        logging.error(e)

@app.route("/haussteuerung", methods=["POST", "GET"])
def hausSteuerung():

    #Für GEG nur die Website anzeigen, bei POST das jeweilige Item in die Queue und loggen
    if request.method == "GET":
        logging.info("   -GET Haussteuerung User: {}".format(str(request.remote_addr)))
        return render_template("haussteuerung.html", async_mode=socketio.async_mode)
    else:
        if request.form.get("rollo") == "upAll":
            logging.info("   -POST Haussteuerung allUp User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_ALL)

        elif request.form.get("rollo") == "downAll":
            logging.info("   -POST Haussteuerung allDown User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_ALL)

        elif request.form.get("fan") == "fanOnShort":
            logging.info("   -POST Haussteuerung fanOn Short User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Fan.START_FAN_SHORT)

        elif request.form.get("fan") == "fanOnLong":
            logging.info("   -POST Haussteuerung fanOn Long User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Fan.START_FAN_LONG)

        elif request.form.get("fan") == "fanOff":
            logging.info("   -POST Haussteuerung fanOff User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Fan.STOP_FAN)

        elif request.form.get("radio") == "radioOnShort":
            logging.info("   -POST Haussteuerung radioOn Short User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Radio.START_RADIO_SHORT)

        elif request.form.get("radio") == "radioOnLong":
            logging.info("   -POST Haussteuerung radioOn Long User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Radio.START_RADIO_LONG)

        elif request.form.get("radio") == "radioOff":
            logging.info("   -POST Haussteuerung radioOff User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Radio.STOP_RADIO)

        elif request.form.get("pump") == "pumpOn":
            logging.info("   -POST Haussteuerung pumpOn User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Pump.START_PUMP)

        elif request.form.get("pump") == "pumpOff":
            logging.info("   -POST Haussteuerung pumpOff User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Pump.STOP_PUMP)

        elif request.form.get("alarm") == "alarmOn":
            logging.info("   -POST Haussteuerung alarmOn User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Alarm.START_ALARM)

        elif request.form.get("alarm") == "alarmOff":
            logging.info("   -POST Haussteuerung alarmOff User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.Alarm.STOP_ALARM)

        return render_template("haussteuerung.html",async_mode=socketio.async_mode)


@socketio.on("haussteuerungDataGetEvent")
def handleHausSteuerungDataEvent():
    #Die jeweiligen Daten zur Website schicken, um mit Javascript etwas dynamic reinzubringen
    pumpShouldBeOff = False
    if db.pump.lastTimeRunned + timedelta(milliseconds=db.Pump.PUMP_INTERVALL_FOR_NEXT_RUN) > datetime.now():
        pumpShouldBeOff = True

    someRolloIsRunning = False
    for key, room in db.house.items():
        if room.rollStatus != db.Room.ROLLSTATUS_IDLE:
            someRolloIsRunning = True
            break

    dataToWebSite = {}
    dataToWebSite.update({"rolloStatus":someRolloIsRunning})
    dataToWebSite.update({"pumpStatus":db.pump.pumpIsOn})
    dataToWebSite.update({"fanStatus":db.fan.fanIsOn})
    dataToWebSite.update({"radioStatus":db.radio.radioIsOn})
    dataToWebSite.update({"pumpShouldBeOff":pumpShouldBeOff})
    dataToWebSite.update({"alarmStatus":db.alarm.alarmIsOn})
    dataToWebSite.update({"alarmCanStart":db.alarm.alarmCanStart})

    emit("haussteuerungDataSendEvent", dataToWebSite, broadcast=True)



@app.route("/hauszeiten", methods=["POST", "GET"])
def rolladenTimer():

    currentTime = datetime.now()
    today = datetime.now().weekday()
    tomorrow = (today+1) % 7
    today = str(today)
    tomorrow = str(tomorrow)

    webSunTimes = {"today":db.sunTime.sunTimes[today] , "tomorrow":db.sunTime.sunTimes[tomorrow]}

    if request.method == "GET":
        logging.info("   -GET HAUSZEITEN User: {}".format(str(request.remote_addr)))
    else:
        logging.info("   -POST HAUSZEITEN User: {}".format(str(request.remote_addr)))

        try:
            db.houseTime.offSetMorning = int(request.form.get("offSetMorning"))
            db.houseTime.offSetEvening = int(request.form.get("offSetEvening"))
        except BaseException as e:
            logging.info(str(e))
            db.houseTime.offSetMorning = 0
            db.houseTime.offSetEvening = 0

        #Alle Tage durchgehen
        for x in range(0,7):

            upTime = request.form.get("{}UpTime".format(str(x)))
            downTime = request.form.get("{}DownTime".format(str(x)))

            #Error checking
            if upTime == "" and downTime == "":
                continue
            elif upTime == "" and downTime != "":
                db.houseTime.setDownTime(currentTime, downTime, x)
                continue
            elif upTime != "" and downTime == "":
                db.houseTime.setUpTime(currentTime, upTime, x)
            else:
                db.houseTime.setDownTime(currentTime, downTime, x)
                db.houseTime.setUpTime(currentTime, upTime, x)

        db.houseTime.writeHouseTimeToTextFile()

        # in setXXXXXTimeParameters ist der dritte Wert "", weil alle Räume gleichzeitig 
        #für jedes Zimmer überprüfen, welche Zeit gesetzt werden soll
        #False, weil individuell nicht gesetzt wird
        #"" damit die checkbox in /rolladen nicht gestzt wird
        #eine einheitliche Randomzeit setzen
        randNum = randint(-db.Room.RANDOM_RANGE, db.Room.RANDOM_RANGE)

        for key, room in db.house.items():
            if room.gotOwnUpTime == "checked":
                room.setUpTimeParameters(room.upTimeWebSite, True,room.gotOwnUpTime, room.allowUpToday)
            else:
                if currentTime.replace(hour=int(db.houseTime.getTodayUpTime(currentTime)[0:2]), minute=int(db.houseTime.getTodayUpTime(currentTime)[3:5]), second=0) > \
                currentTime.replace(hour=int(db.sunTime.getTodaySunRise(currentTime)[0:2]), minute=int( db.sunTime.getTodaySunRise(currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetMorning):
                    room.setUpTimeParameters(db.houseTime.getTodayUpTime(currentTime), False, room.gotOwnUpTime, room.allowUpToday, randNum)
                else:
                    upTime = currentTime.replace(hour=int(db.sunTime.getTodaySunRise(currentTime)[0:2]), minute=int( db.sunTime.getTodaySunRise(currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetMorning)
                    upTimeStr = upTime.strftime("%H:%M")
                    room.setUpTimeParameters(upTimeStr, False ,room.gotOwnUpTime, room.allowUpToday, randNum)

            if room.gotOwnDownTime == "checked":
                room.setDownTimeParameters(room.downTimeWebSite,True,  room.gotOwnDownTime, room.allowDownToday)
            else:
                if currentTime.replace(hour=int(db.houseTime.getTodayDownTime(currentTime)[0:2]), minute=int(db.houseTime.getTodayDownTime(currentTime)[3:5]), second=0) < \
                currentTime.replace(hour=int(db.sunTime.getTodaySunSet(currentTime)[0:2]), minute=int( db.sunTime.getTodaySunSet(currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetEvening):
                    room.setDownTimeParameters(db.houseTime.getTodayDownTime(currentTime), False,  room.gotOwnDownTime, room.allowDownToday, randNum)
                else:
                    downTime = currentTime.replace(hour=int(db.sunTime.getTodaySunSet(currentTime)[0:2]), minute=int( db.sunTime.getTodaySunSet(currentTime)[3:5]), second=0) + timedelta(minutes = db.houseTime.offSetEvening)
                    downTimeStr = downTime.strftime("%H:%M")
                    room.setDownTimeParameters(downTimeStr, False, room.gotOwnDownTime, room.allowDownToday, randNum)

    return render_template("hauszeiten.html",async_mode=socketio.async_mode,  houseTime=db.houseTime.houseTimes, sunTimes=webSunTimes, offSetMorning = str(db.houseTime.offSetMorning), offSetEvening = str(db.houseTime.offSetEvening))


@app.route("/rolladen", methods=["POST", "GET"])
def rolladen():
    if request.method == "GET":
        logging.info("   -GET ROLLADEN User: {}".format(str(request.remote_addr)))
        return render_template("rolladen.html",async_mode=socketio.async_mode,  house = db.house)
    elif request.method == "POST":
        logging.info("   -POST ROLLADEN User: {}".format(str(request.remote_addr)))
        if request.form.get("up") == db.Room.JAN:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.JAN, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_JAN)

        elif request.form.get("up") == db.Room.LEA_SLEEP:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.LEA_SLEEP, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_LEA_SLEEP)

        elif request.form.get("up") == db.Room.LEA_LIVING:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.LEA_LIVING, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_LEA_LIVING)

        elif request.form.get("up") == db.Room.PARENTS:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.PARENTS, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_PARENTS)

        elif request.form.get("up") == db.Room.TOILET:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.TOILET, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_TOILET)

        elif request.form.get("up") == db.Room.GUEST_TOILET:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.GUEST_TOILET, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_GUEST_TOILET)

        elif request.form.get("up") == db.Room.KITCHEN:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.KITCHEN, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_KITCHEN)

        elif request.form.get("up") == db.Room.TERRA_RIGHT:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.TERRA_RIGHT, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_TERRA_RIGHT)

        elif request.form.get("up") == db.Room.TERRA_LEFT:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.TERRA_LEFT, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_TERRA_LEFT)

        elif request.form.get("up") == db.Room.LIVING_GARAGE:
            logging.info("   -UP ROLLADEN {} User: {}".format(db.Room.LIVING_GARAGE, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.UP_LIVING_GARAGE)

        #-----DOWN------

        elif request.form.get("down") == db.Room.JAN:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.JAN, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_JAN)

        elif request.form.get("down") == db.Room.LEA_SLEEP:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.LEA_SLEEP, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_LEA_SLEEP)

        elif request.form.get("down") == db.Room.LEA_LIVING:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.LEA_LIVING, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_LEA_LIVNG)

        elif request.form.get("down") == db.Room.PARENTS:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.PARENTS, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_PARENTS)

        elif request.form.get("down") == db.Room.TOILET:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.TOILET, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_TOILET)

        elif request.form.get("down") == db.Room.GUEST_TOILET:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.GUEST_TOILET, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_GUEST_TOILET)

        elif request.form.get("down") == db.Room.KITCHEN:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.KITCHEN, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_KITCHEN)

        elif request.form.get("down") == db.Room.TERRA_RIGHT:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.TERRA_RIGHT, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_TERRA_RIGHT)

        elif request.form.get("down") == db.Room.TERRA_LEFT:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.TERRA_LEFT, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_TERRA_LEFT)

        elif request.form.get("down") == db.Room.LIVING_GARAGE:
            logging.info("   -DOWN ROLLADEN {} User: {}".format(db.Room.LIVING_GARAGE, str(request.remote_addr)))
            db.myQueue.put_nowait(db.Room.DOWN_LIVING_GARAGE)

        return render_template("rolladen.html", async_mode=socketio.async_mode)


@socketio.on("rolladenDataGetEvent")
def handleRolladenDataEvent():
    dataToWebSite = {}

    for key, room in db.house.items():
        temp = {key:room.rollStatus}
        dataToWebSite.update(temp)
        del temp

    emit("rolladenDataSendEvent", dataToWebSite, broadcast = True)


@app.route("/zimmerzeiten", methods=["POST", "GET"])
def zimmerzeiten():

    if request.method == "GET":
        logging.info("   -GET ZIMMERZEITEN User: {}".format(str(request.remote_addr)))
        return render_template("zimmerzeiten.html",async_mode=socketio.async_mode,  house = db.house)

    elif request.method == "POST":
        if request.form.get("saveTimeButton") == "saveTime":
            logging.info("   -SAVETIME ZIMMERZEITEN User: {}".format(str(request.remote_addr)))

            try:
                with open("roomTimes.csv", "w") as file:
                    writer = csv.writer(file)
                    writer.writerow(["name", "upTime", "upTimeWebSite", "gotOwnUpTime", "allowUpToday", "downTime", "downTimeWebSite", "gotOwnUpTime", "allowDownToday"])
                    rowToWrite = []

                    for key, room in db.house.items():
                        #get Time and CheckBox Value
                        upTime = request.form.get("{}UpTime".format(room.name))
                        downTime = request.form.get("{}DownTime".format(room.name))

                        #checkbox werte wieder casten
                        upTimeCheckBox = request.form.get("{}UpTimeCheckBox".format(room.name))
                        upTimeCheckBox = "checked" if upTimeCheckBox == "on" else ""

                        allowUpCheckBox = request.form.get("{}AllowUpCheckBox".format(room.name))
                        allowUpCheckBox = "checked" if allowUpCheckBox == "on" else ""

                        downTimeCheckBox = request.form.get("{}DownTimeCheckBox".format(room.name))
                        downTimeCheckBox = "checked" if downTimeCheckBox == "on" else ""

                        allowDownCheckBox = request.form.get("{}AllowDownCheckBox".format(room.name))
                        allowDownCheckBox = "checked" if allowDownCheckBox == "on" else ""

                        #entsprechende Werte setzen
                        if downTime != "" and upTime != "":
                            room.setUpTimeParameters(upTime, True,  upTimeCheckBox, allowUpCheckBox)
                            room.setDownTimeParameters(downTime, True,  downTimeCheckBox, allowDownCheckBox)
                        elif downTime != "" and upTime == "":
                            room.setDownTimeParameters(downTime, True,  downTimeCheckBox, allowDownCheckBox)
                        elif downTime == "" and upTime != "":
                            room.setUpTimeParameters(upTime, True,  upTimeCheckBox, allowUpCheckBox)
                        else:
                            continue

                        rowToWrite.append(room.name)
                        rowToWrite.append(room.upTime)
                        rowToWrite.append(room.upTimeWebSite)
                        rowToWrite.append(room.gotOwnUpTime)
                        rowToWrite.append(room.allowUpToday)
                        rowToWrite.append(room.downTime)
                        rowToWrite.append(room.downTimeWebSite)
                        rowToWrite.append(room.gotOwnDownTime)
                        rowToWrite.append(room.allowDownToday)
                        writer.writerow(rowToWrite)
                        rowToWrite.clear()

            except BaseException as e:
                logging.error("     - Error Write individual Room Time")
                logging.error(e)
        return render_template("zimmerzeiten.html", async_mode=socketio.async_mode,  house = db.house)



#-----PUMPE WEBSITE

@app.route("/pumpe", methods=["POST", "GET"])
def pumpe():
    if request.method == "POST":
        if request.form.get("pumpButton") == "savePumpTime":
            logging.info("   -POST Pumpe savePumpTime User: {}".format(str(request.remote_addr)))
            #durch alle Tage iterieren
            for x in range(0,7):                
                pumpTime = request.form.get("{}PumpTime".format(str(x)))

                if pumpTime == "":
                    continue

                checkbox = request.form.get("{}CheckBox".format(str(x)))
                checkbox = "checked" if checkbox == "on" else ""

                #wenn die aktuelle Pumpzeit unterschiedlich zur alten ist, soll das gemerkt werden in [2]
                if db.pump.pumpTime[str(x)][0] != pumpTime or db.pump.pumpTime[str(x)][1] != checkbox:
                    logging.info("   -POST Pump CheckBox or Time Value Changed User: {}".format(str(request.remote_addr)))
                    db.pump.pumpTime[str(x)][0] = pumpTime
                    db.pump.pumpTime[str(x)][1] = checkbox
                    db.pump.pumpTime[str(x)][2] = db.pump.NEED_TO_UPDATE

        elif request.form.get("pumpButton") == "pumpOff":
            logging.info("   -POST Pumpe PumpOff User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.pump.STOP_PUMP)

        else:
            logging.info("   -POST Pumpe PumpOn User: {}".format(str(request.remote_addr)))
            db.myQueue.put_nowait(db.pump.START_PUMP)

        db.pump.writePumpTimeToTextFile()

        return render_template("pumpe.html",  async_mode=socketio.async_mode, content = db.pump.pumpTime)
    else:
        logging.info("   -GET Pumpe User: {}".format(str(request.remote_addr)))
        return render_template("pumpe.html",  async_mode=socketio.async_mode, content = db.pump.pumpTime)

    #WebSocket
@socketio.on("pumpDataGetEvent")
def handlePumpDataEvent():

    pumpShouldBeOff = False
    if db.pump.lastTimeRunned + timedelta(milliseconds=db.Pump.PUMP_INTERVALL_FOR_NEXT_RUN) > datetime.now():
        pumpShouldBeOff = True

    dataToWebSite = {}
    dataToWebSite.update({"pumpStatus":db.pump.pumpIsOn})
    dataToWebSite.update({"pumpShouldBeOff":pumpShouldBeOff})

    emit("pumpDataSendEvent", dataToWebSite, broadcast=True)


#-----MAIN
if __name__ == "__main__":
    myThread = None
    try:
        logging.info("     -START")
        logger = logging.getLogger()

        #einen Loghandler erstellen, der nach 7 Tagen die Log Datei löscht und immer einen BackupCount von 10 Dateien zulässt
        logHandler = TimedRotatingFileHandler(filename="logs.log", when="D", interval=3, backupCount=10, encoding="utf-8", delay=False)

        logFormatter = Formatter(fmt="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        logHandler.setFormatter(logFormatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(logHandler)
        logging.info("Start Of Programm")


        db.init()
        sleep(1)
        houseController = HouseController()

        myThread = Thread(target=houseController.houseControlling, name="HOUSECONTROLLER")
        myThread.daemon = True
        myThread.start()

        socketio.run(app, host="0.0.0.0", port="t.b.d")
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        logging.info(str(e))
    finally:
        db.myQueue.put_nowait(db.STOP_THREAD)
        myThread.join()
        logging.info("     -END")

