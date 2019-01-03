'''
This script will calculate and save the "Time of day" and the "Solar time" of the day to items.
"Time of day" can be morning, day, evening or night. These are clock dependent.
"Solar time" can be dawn, day, dusk and night. These are dependent of the sun's position relative the horizon.
So depending on where you live and the season, the solar time might be "day" while time of day is "night"
and vice versa.
This topic by Rich Koshak might also be of interest: https://community.openhab.org/t/design-pattern-time-of-day/15407/4
Prerequisits:
=============================
- Astro binding installed.
- Download to openHAB maps directory: en_timeOfDay.map and en_solartime.map
  From https://github.com/OH-Jython-Scripters/lucid/tree/master/transform
- Persistence set up. The item group named G_PersistOnChange is persisted on change
- In the lucid config file, configure at what time morning, day, evening and night starts,
  have a look at https://github.com/OH-Jython-Scripters/lucid/blob/master/automation/lib/python/lucid/example_self.config.py
- Items as defined below. (You may use other names but then you'll get extra work every time you update the script.)
Group G_PersistOnChange // Set up for persistence on change and system start up
Number V_SolarTime "Solar time of day [MAP(en_solartime.map):%s]" <sun> (G_PersistOnChange)
Number V_TimeOfDay "Time of day [MAP(en_timeOfDay.map):%s]" <sun> (G_PersistOnChange)
Number Sun_Position_Azimuth "Sun azimuth" <sun> {channel="astro:sun:local:position#azimuth"}
Number Sun_Position_Elevation "Sun elevation" <sun> {channel="astro:sun:local:position#elevation"}
DateTime V_CivilDawn "Civil Dawn [%1$tH:%1$tM]" <flow> (G_PersistOnChange) {channel="astro:sun:local:civilDawn#start"}
DateTime V_Sunrise "Sunrise [%1$tH:%1$tM]" <sun> (G_PersistOnChange) {channel="astro:sun:local:rise#start"}
DateTime V_Sunset "Sunset [%1$tH:%1$tM]" <sun> (G_PersistOnChange) {channel="astro:sun:local:set#start"}
DateTime V_CivilDuskStart "Civil dusk [%1$tH:%1$tM]" <flow> (G_PersistOnChange) {channel="astro:sun:local:civilDusk#start"}
DateTime V_CivilDuskEnd "Nautical dusk [%1$tH:%1$tM]" <moon> (G_PersistOnChange) {channel="astro:sun:local:civilDusk#end"}
'''

from core.rules import rule
from core.triggers import ChannelEventTrigger, StartupTrigger, CronTrigger
from core.utils import postUpdateCheckFirst
from configuration import SOLARTIME, TIMEOFDAY, kw, greetings
import time
import org.joda.time.DateTime as DateTime

def greeting():
    # To use this, you should set up astro.py as described
    # here https://github.com/OH-Jython-Scripters/lucid/blob/master/Script%20Examples/astro.py
    # It will take care of updating the item 'V_TimeOfDay' for you
    timeOfDay = getItemValue('V_TimeOfDay', TIMEOFDAY['DAY'])
    if timeOfDay in config.greeting:
        return config.greeting[timeOfDay]
    else:
return 'good day'

@rule("Example time of day calculation")
class TimeOfDayCalc(object):
    """
    Regardless of the sun, this rule determines what is day and night
    """
    def getEventTriggers(self):
        return [
            CronTrigger('9 ' + str(self.config.timeOfDay['morningStart']['Minute']) + ' ' + str(self.config.timeOfDay['morningStart']['Hour']) + ' * * ?'), # E.g. 9 seconds after morning starts
            CronTrigger('9 ' + str(self.config.timeOfDay['dayStart']['Minute']) + ' ' + str(self.config.timeOfDay['dayStart']['Hour']) + ' * * ?'), # E.g. 9 seconds after day starts
            CronTrigger('9 ' + str(self.config.timeOfDay['eveningStart']['Minute']) + ' ' + str(self.config.timeOfDay['eveningStart']['Hour']) + ' * * ?'), # E.g. 9 seconds after evening starts
            CronTrigger('9 ' + str(self.config.timeOfDay['nightStart']['Minute']) + ' ' + str(self.config.timeOfDay['nightStart']['Hour']) + ' * * ?'), # E.g. 9 seconds after night starts
            StartupTrigger()
        ]

    def execute(self, modules, inputs):
        self.log.setLevel(INFO)
        #self.log.setLevel(DEBUG)

        # Get the time period start times for today
        now = DateTime()
        morningStart = now.withTime(self.config.timeOfDay['morningStart']['Hour'],self.config.timeOfDay['morningStart']['Minute'],0,0).toInstant()
        dayStart = now.withTime(self.config.timeOfDay['dayStart']['Hour'],self.config.timeOfDay['dayStart']['Minute'],0,0).toInstant()
        eveningStart = now.withTime(self.config.timeOfDay['eveningStart']['Hour'],self.config.timeOfDay['eveningStart']['Minute'],0,0).toInstant()
        nightStart = now.withTime(self.config.timeOfDay['nightStart']['Hour'],self.config.timeOfDay['nightStart']['Minute'],0,0).toInstant()

        timeOfDay = TIMEOFDAY['NIGHT']
        if (now.isAfter(morningStart) and now.isBefore(dayStart)):
            timeOfDay = TIMEOFDAY['MORNING']
        elif (now.isAfter(dayStart) and now.isBefore(eveningStart)):
            timeOfDay = TIMEOFDAY['DAY']
        elif (now.isAfter(eveningStart) and now.isBefore(nightStart)):
            timeOfDay = TIMEOFDAY['EVENING']

        if postUpdateCheckFirst('V_TimeOfDay', timeOfDay):
            self.log.debug("Time of day now: " + kw(TIMEOFDAY, timeOfDay))

@rule("Example Astro Channel rule", description="This doc comment will become the ESH Rule documentation value for Paper UI")
@when("Channel astro:sun:local:civilDawn#event triggered START")
@when("Channel astro:sun:local:rise#event triggered START")
@when("Channel astro:sun:local:set#event triggered START")
@when("Channel astro:sun:local:civilDusk#event triggered START")
@when("Channel astro:sun:local:civilDusk#event triggered END")
def exampleTimeOfDay(event):
    dawn_start = ir.get('V_CivilDawn').getState().calendar.timeInMillis
    day_start = ir.get('V_Sunrise').getState().calendar.timeInMillis
    dusk_start = ir.get('V_CivilDuskStart').getState().calendar.timeInMillis
    night_start = ir.get('V_CivilDuskEnd').getState().calendar.timeInMillis
    curr = None
    self.log.debug('dawn_start : ' + str(dawn_start))
    self.log.debug('day_start  : ' + str(day_start))
    self.log.debug('dusk_start : ' + str(dusk_start))
    self.log.debug('night_start: ' + str(night_start))
    time.sleep(2) # We seem to need this
    now = DateTime().getMillis()
    self.log.debug('now        : ' + str(now))

    if now >= dawn_start and now < day_start:
        curr = SOLARTIME['DAWN']
    elif now >= day_start and now < dusk_start:
        curr = SOLARTIME['DAY']
    elif now >= dusk_start and now < night_start:
        curr = SOLARTIME['DUSK']
    else:
        curr = SOLARTIME['NIGHT']

    if postUpdateCheckFirst('V_SolarTime', curr):
        self.log.info(u"Solar time is now: " + kw(SOLARTIME, curr))

