from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun

import logging

class SunTimeHandler:

    def __init__(self):
        #Sonnenaufgang Sonnenuntergang
        self.sunTimes = {"0":["",""], "1":["",""], "2":["",""], "3":["",""], "4":["",""], "5":["",""], "6":["",""] }
        self.latitude = "t.b.d"
        self.longitude = "t.b.d"
        self.city = LocationInfo(timezone="Europe/Berlin",latitude=self.latitude, longitude=self.longitude)

    def getTodaySunRise(self, currentTime):
        return self.sunTimes[str(currentTime.weekday())][0]

    def getTodaySunSet(self, currentTime):
        return self.sunTimes[str(currentTime.weekday())][1]

    def setSuntime(self):

        loopDate = datetime.now()

        for i in range(0,7):
            #Wochentagsindex
            loopDayIndex = loopDate.weekday()

            #Sonnenaufgang Sonnenuntergang berechnen
            mySun = sun(self.city.observer, tzinfo=self.city.timezone, date=loopDate)
            sunrise = mySun["sunrise"]
            sunset = mySun["sunset"]

            sunrise = sunrise.strftime("%H:%M")
            sunset = sunset.strftime("%H:%M")

            self.sunTimes[str(loopDayIndex)] = [sunrise, sunset]
            loopDate = loopDate + timedelta(days=1)

        logging.info("     - SunTime: %s", self.sunTimes)

