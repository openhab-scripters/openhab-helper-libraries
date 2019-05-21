'''
PURPOSE:
This example rule will adjust a Mode Item based on the time of day. If the
Mode Item is manually changed to something that is not included the OD,
such as 'Party', the Mode will not be updated and will need to be manually
changed back to a Mode included in the OD.

REQUIRES:
- a Mode StringItem
- the time_of_day OrderedDict (OD) added to the configuration.py

String Mode "Mode [%s]" <house> 
'''
from core.rules import rule
from core.triggers import when
from org.joda.time import DateTime, Interval
from configuration import time_of_day

def modeTriggerGenerator(modeTimes):
    from core.triggers import when
    def generatedTriggers(function):
        for mode in list(modeTimes.keys()):
            when("Time cron {} {} {} * * ?".format(modeTimes[mode]['second'], modeTimes[mode]['minute'], modeTimes[mode]['hour']))(function)
        return function
    return generatedTriggers

@rule("Cron: Update Mode")
@when("System started")
@modeTriggerGenerator(time_of_day)
def updateMode(event):
    lastModeOfDay = time_of_day.items()[-1][0]
    newMode = lastModeOfDay
    for i, (mode, value) in enumerate(time_of_day.iteritems()):
        if i < len(time_of_day) - 1:
            modeInterval = Interval(DateTime.now().withTime(value['hour'],
                                                            value['minute'],
                                                            value['second'],
                                                            0),
                                           DateTime.now().withTime(time_of_day.items()[i + 1][1]['hour'],
                                                                   time_of_day.items()[i + 1][1]['minute'],
                                                                   time_of_day.items()[i + 1][1]['second'],
                                                                   0))
            if modeInterval.contains(DateTime.now()):
                newMode = mode
                break
    if items["Mode"] != StringType(newMode) and (str(items["Mode"]) in timeIntervals.keys() + [lastModeOfDay] or items["Mode"] == UnDefType.NULL):
        updateMode.log.debug("Mode changed from [{}] to [{}]".format(items["Mode"], newMode))
        events.sendCommand("Mode", newMode)
    else:
        updateMode.log.debug("Job ran but current Mode [{}] did not need to be changed: [{}]".format(items["Mode"], newMode))

'''
PURPOSE:
The following two rules will calculate and save the "Time of day" and the "Solar time" of the day to items.
"Time of day" can be morning, day, evening or night. These are clock dependent.
"Solar time" can be dawn, day, dusk and night. These are dependent of the sun's position relative the horizon.
So depending on where you live and the season, the solar time might be "day" while time of day is "night"
and vice versa. This topic by Rich Koshak might also be of interest: 
https://community.openhab.org/t/design-pattern-time-of-day/15407/4

REQUIRES:
- Astro binding installed.
- Download to openHAB maps directory: en_timeOfDay.map and en_solartime.map
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
import time

from core.rules import rule
from core.triggers import when
from core.utils import postUpdateCheckFirst, kw
from configuration import timeOfDay, SOLARTIME, TIMEOFDAY

from org.joda.time import DateTime

@rule("Example time of day calculation", description="Regardless of the sun, this rule determines what is day and night")
@when("System started")
@when("9 " + str(timeOfDay['morningStart']['Minute']) + ' ' + str(timeOfDay['morningStart']['Hour']) + ' * * ?')
@when("9 " + str(timeOfDay['dayStart']['Minute']) + ' ' + str(timeOfDay['dayStart']['Hour']) + ' * * ?')
@when("9 " + str(timeOfDay['eveningStart']['Minute']) + ' ' + str(timeOfDay['eveningStart']['Hour']) + ' * * ?')
@when("9 " + str(timeOfDay['nightStart']['Minute']) + ' ' + str(timeOfDay['nightStart']['Hour']) + ' * * ?')
def exampleTimeOfDay(event):
    # Get the time period start times for today
    now = DateTime.now()
    morningStart = now.withTime(timeOfDay['morningStart']['Hour'],timeOfDay['morningStart']['Minute'],0,0).toInstant()
    dayStart = now.withTime(timeOfDay['dayStart']['Hour'],timeOfDay['dayStart']['Minute'],0,0).toInstant()
    eveningStart = now.withTime(timeOfDay['eveningStart']['Hour'],timeOfDay['eveningStart']['Minute'],0,0).toInstant()
    nightStart = now.withTime(timeOfDay['nightStart']['Hour'],timeOfDay['nightStart']['Minute'],0,0).toInstant()

    timeOfDay = TIMEOFDAY['NIGHT']
    if (now.isAfter(morningStart) and now.isBefore(dayStart)):
        timeOfDay = TIMEOFDAY['MORNING']
    elif (now.isAfter(dayStart) and now.isBefore(eveningStart)):
        timeOfDay = TIMEOFDAY['DAY']
    elif (now.isAfter(eveningStart) and now.isBefore(nightStart)):
        timeOfDay = TIMEOFDAY['EVENING']

    if postUpdateCheckFirst('V_TimeOfDay', timeOfDay):
        exampleTimeOfDay.log.debug("Time of day now: [{}]".format(kw(TIMEOFDAY, timeOfDay)))

@rule("Example Astro Channel rule", description="This will become the Rule description displayed in Paper UI")
@when("Channel astro:sun:local:civilDawn#event triggered START")
@when("Channel astro:sun:local:rise#event triggered START")
@when("Channel astro:sun:local:set#event triggered START")
@when("Channel astro:sun:local:civilDusk#event triggered START")
@when("Channel astro:sun:local:civilDusk#event triggered END")
def exampleSolarTimeOfDay(event):
    time.sleep(2) # wait for Items to update
    dawn_start = DateTime(items['V_CivilDawn'].toString())
    day_start = DateTime(items['V_Sunrise'].toString())
    dusk_start = DateTime(items['V_CivilDuskStart'].toString())
    night_start = DateTime(items['V_CivilDuskEnd'].toString())

    curr = None
    now = DateTime.now()
    exampleSolarTimeOfDay.log.debug("dawn_start  [{}]".format(dawn_start))
    exampleSolarTimeOfDay.log.debug("day_start   [{}]".format(day_start))
    exampleSolarTimeOfDay.log.debug("dusk_start  [{}]".format(dusk_start))
    exampleSolarTimeOfDay.log.debug("night_start [{}]".format(night_start))
    exampleSolarTimeOfDay.log.debug("now         [{}]".format(now))

    if now.isAfter(dawn_start) and now.isBefore(day_start):
        curr = SOLARTIME['DAWN']
    elif now.isAfter(day_start) and now.isBefore(dusk_start):
        curr = SOLARTIME['DAY']
    elif now.isAfter(dusk_start) and now.isBefore(night_start):
        curr = SOLARTIME['DUSK']
    else:
        curr = SOLARTIME['NIGHT']

    if postUpdateCheckFirst('V_SolarTime', curr):
        exampleSolarTimeOfDay.log.info("Solar time is now [{}]".format(kw(SOLARTIME, curr)))