import weakref # Using this to prevent problems with garbage collection
from org.joda.time import DateTime

from core.jsr223 import scope
from core.date import format_date
from core.log import logging, LOG_PREFIX
from core.utils import isActive, getItemValue, postUpdateCheckFirst, sendCommandCheckFirst, kw
from core.actions import PersistenceExtensions
from configuration import customDateTimeFormats
from personal.idealarm import custom

log = logging.getLogger(LOG_PREFIX + '.ideAlarm')
ZONESTATUS = {'NORMAL': 0, 'ALERT': 1, 'ERROR': 2, 'TRIPPED': 3, 'ARMING': 4}
ARMINGMODE = {'DISARMED': 0, 'ARMED_HOME': 1, 'ARMED_AWAY': 2}

class IdeAlarmError(Exception):
    '''
    Base class for IdeAlarm errors
    '''

class IdeAlarmSensor(object):
    '''
    Alarm Sensor Object
    '''
    def __init__(self, parent, cfg):
        '''
        Initialise the IdeAlarmSensor class

        Expects:
         - Parent object
         - cfg (dictionary) The sensor's configuration dictionary
        '''
        self.name = cfg['name']
        _label = scope.itemRegistry.getItem(self.name).label
        self.label = _label if _label is not None else 'Sensor has no label'
        self.parent = weakref.ref(parent) # <= garbage-collector safe!
        self.sensorClass = cfg['sensorClass']
        self.nag = cfg['nag']
        self.nagTimeoutMins = cfg['nagTimeoutMins']
        self.armWarn = cfg['armWarn']
        self.enabled = cfg['enabled']
        self.log = logging.getLogger(u"{}.IdeAlarmSensor.{}".format(LOG_PREFIX, self.name.decode('utf8')))
        #self.log.info(u"ideAlarm sensor {} initialized...".format(self.name.decode('utf8')))

    def isEnabled(self):
        '''
        The sensor can be enabled/disabled in the configuration file by a boolean or a function.
        '''
        if callable(self.enabled):
            return self.enabled(scope.events, self.log)
        else:
            return self.enabled

    def isActive(self):
        '''
        The sensor is considered active when its OPEN, ON or NULL. Locks are different.
        '''
        return isActive(scope.itemRegistry.getItem(self.name))

    def getLastUpdate(self):
        '''
        Returns the sensors last update time (if available).
        type is 'org.joda.time.DateTime', http://joda-time.sourceforge.net/apidocs/org/joda/time/DateTime.html
        '''
        try:
            lastUpdate = PersistenceExtensions.lastUpdate(scope.itemRegistry.getItem(self.name)).toDateTime()
        except:
            lastUpdate = DateTime(0)
            self.log.info(u"Could not retrieve persistence data for sensor: {}".format(self.name.decode('utf8')))
        return lastUpdate


class IdeAlarmZone(object):
    '''
    Alarm Zone Object
    '''
    def __init__(self, parent, zoneNumber, cfg):
        '''
        Initialise the IdeAlarmZone class

        Expects:
         - Parent object
         - zoneNumber (integer) The zone's ordinal number
         - cfg (dictionary) The zone's configuration dictionary
        '''
        self._armingMode = None
        self._zoneStatus = None
        self.zoneNumber = zoneNumber
        self.alertDevices = cfg['alertDevices']
        self.name = cfg['name']
        self.armAwayToggleSwitch = cfg['armAwayToggleSwitch']
        self.armHomeToggleSwitch = cfg['armHomeToggleSwitch']
        self.mainZone = cfg['mainZone']
        self.canArmWithTrippedSensors = cfg['canArmWithTrippedSensors']
        self.alarmTestMode = parent.alarmTestMode
        self.parent = weakref.ref(parent) # <= garbage-collector safe!
        self.log = logging.getLogger(u"{}.IdeAlarmZone.Zone.{}".format(LOG_PREFIX, self.zoneNumber))
        self.sensors = []
        for sensor in cfg['sensors']:
            self.sensors.append(IdeAlarmSensor(self, sensor))
        self.armingModeItem = cfg['armingModeItem']
        self.statusItem = cfg['statusItem']

        self.openSections = self.countOpenSections()
        self.setArmingMode(getItemValue(self.armingModeItem, ARMINGMODE['DISARMED'])) # Will also set the zone status to normal
        self.log.info(u"ideAlarm Zone {} initialized with {} open sensors".format(self.name.decode('utf8'), self.openSections))

    def getArmingMode(self):
        '''
        Returns the zones current arming mode
        '''
        return self._armingMode

    def setArmingMode(self, newArmingMode, sendCommand=False):
        '''
        Sets the zones current arming mode
        '''
        oldArmingMode = self._armingMode

        if newArmingMode not in [ARMINGMODE['DISARMED'], ARMINGMODE['ARMED_HOME'], ARMINGMODE['ARMED_AWAY']]:
            raise IdeAlarmError("Trying to set an invalid arming mode: {}".format(newArmingMode))

        # There might be open sensors when trying to arm. If so, the custom function onArmingWithOpenSensors
        # gets called. (That doesn't necessarily need to be an error condition).
        # However if the zone has been configured not to allow opened sensors during arming,
        # the zone status will be set to ERROR and onZoneStatusChange will be able to trap track it down.
        if newArmingMode in [ARMINGMODE['ARMED_AWAY'], ARMINGMODE['ARMED_HOME']] \
        and self.getZoneStatus() != ZONESTATUS['ARMING'] and self.getZoneStatus() is not None \
        and self.openSections > 0:
            if 'onArmingWithOpenSensors' in dir(custom):
                custom.onArmingWithOpenSensors(self, newArmingMode)
            if not self.canArmWithTrippedSensors:
                self.setZoneStatus(ZONESTATUS['ERROR'], errorMessage='Arming is not allowed with open sensors')
                self.log.warn(u"Zone \'{}'\' can not be set to new arming mode: {} due to that there are open sensors!".format(self.name.decode('utf8'), kw(ARMINGMODE, newArmingMode)))
                import time
                time.sleep(1)
                self.setZoneStatus(ZONESTATUS['NORMAL'])
                return

        # Don't set arming mode to 'ARMED_AWAY' immediately, we need to wait for the exit timer
        # self.getZoneStatus() returns None when initializing
        if newArmingMode == ARMINGMODE['ARMED_AWAY'] \
        and self.getZoneStatus() is not None and self.getZoneStatus() != ZONESTATUS['ARMING']:
            self.setZoneStatus(ZONESTATUS['ARMING'])
            postUpdateCheckFirst("Z{}_Exit_Timer".format(self.zoneNumber), scope.ON)
            return
        self._armingMode = newArmingMode

        # Sync the Item
        postUpdateCheckFirst(self.armingModeItem, newArmingMode, sendCommand)

        # Call custom function if available
        if 'onArmingModeChange' in dir(custom):
            custom.onArmingModeChange(self, newArmingMode, oldArmingMode)

        # Whenever the arming mode is set, reset the zones status to NORMAL
        self.setZoneStatus(ZONESTATUS['NORMAL'])

    def getZoneStatus(self):
        '''
        Returns the zones current status
        '''
        return self._zoneStatus

    def setZoneStatus(self, newZoneStatus, sendCommand=False, errorMessage=None):
        '''
        Sets the zones current status
        '''
        if newZoneStatus not in [ZONESTATUS['NORMAL'], ZONESTATUS['ALERT'], ZONESTATUS['ERROR'], ZONESTATUS['TRIPPED'], ZONESTATUS['ARMING']]:
            raise IdeAlarmError('Trying to set an invalid zone status')
        oldZoneStatus = self._zoneStatus
        self._zoneStatus = newZoneStatus

        if newZoneStatus in [ZONESTATUS['NORMAL']]:

            # Cancel all timers so they won't fire
            postUpdateCheckFirst("Z{}_Entry_Timer".format(self.zoneNumber), scope.OFF)
            postUpdateCheckFirst("Z{}_Exit_Timer".format(self.zoneNumber), scope.OFF)
            postUpdateCheckFirst("Z{}_Alert_Max_Timer".format(self.zoneNumber), scope.OFF)

            # Cancel sirens
            for alertDevice in self.alertDevices:
                sendCommandCheckFirst(alertDevice, scope.OFF)

        # Sync the Zone Status Item
        postUpdateCheckFirst(self.statusItem, newZoneStatus, sendCommand)

        # Call custom function if available
        if 'onZoneStatusChange' in dir(custom):
            custom.onZoneStatusChange(self, newZoneStatus, oldZoneStatus, errorMessage=errorMessage)

    def getOpenSensors(self, mins=0, armingMode=None, isArming=False):
        '''
        Gets all open sensor objects for the zone
        - mins Integer 0-9999 Number of minutes that the sensor must have been
            updated within. A value of 0 will return sensor devices who are
            currently open. 
        - armingMode A sensor is regarded to be open only in the context of an
            arming mode. Defaults to the zones current arming mode.
        - isArming Boolean. In an arming scenario we don't want to include
            sensors that are set not to warn when arming.

        returns a list with open sensor objects.
        '''
        armingMode = self.getArmingMode() if armingMode is None else armingMode
        openSensors = []
        if armingMode == ARMINGMODE['DISARMED']:
            return openSensors
        for sensor in self.sensors:
            if (not sensor.isEnabled()) \
            or (mins == 0 and not sensor.isActive()) \
            or (isArming and not sensor.armWarn) \
            or (mins > 0 and sensor.getLastUpdate().isBefore(DateTime.now().minusMinutes(mins))):
                continue
            if armingMode == ARMINGMODE['ARMED_AWAY'] \
            or (armingMode == ARMINGMODE['ARMED_HOME'] and sensor.sensorClass != 'B'):
                openSensors.append(sensor)
        return openSensors

    def isArmed(self):
        '''
        Returns true if armed, otherwise false
        '''
        return self.getArmingMode() != ARMINGMODE['DISARMED']

    def isDisArmed(self):
        '''Returns true if disarmed, otherwise false'''
        return not self.isArmed()

    def onToggleSwitch(self, itemName):
        '''
        Called whenever an alarm arming mode toggle switch has been switched.
        '''
        newArmingMode = None
        if itemName == self.armAwayToggleSwitch:
            if self.getArmingMode() in [ARMINGMODE['DISARMED']]:
                newArmingMode = ARMINGMODE['ARMED_AWAY']
            else:
                newArmingMode = ARMINGMODE['DISARMED']
        else:
            if self.getArmingMode() in [ARMINGMODE['DISARMED']]:
                newArmingMode = ARMINGMODE['ARMED_HOME']
            else:
                newArmingMode = ARMINGMODE['DISARMED']

        self.log.debug(u"Toggling zone [{}] to new arming mode: [{}]".format(self.name.decode('utf8'), kw(ARMINGMODE, newArmingMode)))
        self.setArmingMode(newArmingMode)

    def onEntryTimer(self):
        '''
        Called whenever the entry timer times out.
        '''
        # Double check that the zone status is tripped, we can probably remove this check later
        if self.getZoneStatus() not in [ZONESTATUS['TRIPPED']]:
            raise IdeAlarmError('Entry Timer timed out but zone status is not tripped')
        self.setZoneStatus(ZONESTATUS['ALERT'])

        # We need to make some noise here!
        if not self.alarmTestMode:
            for alertDevice in self.alertDevices:
                sendCommandCheckFirst(alertDevice, scope.ON)
            self.log.info('You should be able to hear the sirens now...')
        else:
            self.log.info('ALARM_TEST_MODE is activated. No sirens!')
        postUpdateCheckFirst("Z{}_Alert_Max_Timer".format(self.zoneNumber), scope.ON)

    def onExitTimer(self):
        '''
        Exit timer is used when ARMING AWAY only. When the exit timer times out,
        set the zones arming mode
        '''
        self.setArmingMode(ARMINGMODE['ARMED_AWAY'])

    def onAlertMaxTimer(self):
        '''
        Called after the sirens (or whatever alert devices you use) have reached their time limit
        '''
        # Cancel alert devices, e.g. the sirens
        for alertDevice in self.alertDevices:
            sendCommandCheckFirst(alertDevice, scope.OFF)
        self.log.debug('Alert devices have been switched off due to they\'ve reached their time limit')

    def getNagSensors(self, timerTimedOut=False):
        '''
        Check if nagging is required. Performed when a sensor changes its state and when the nag timer ends.
        Nagging is only performed when a zone is disarmed.
        '''
        nagSensors = []
        for sensor in self.sensors:
            if sensor.isEnabled() and sensor.isActive() and sensor.nag and self.getArmingMode() == ARMINGMODE['DISARMED']:
                nagSensors.append(sensor)
        if len(nagSensors) == 0:
            postUpdateCheckFirst("Z{}_Nag_Timer".format(self.zoneNumber), scope.OFF) # Cancel the nag timer
        else:
            postUpdateCheckFirst("Z{}_Nag_Timer".format(self.zoneNumber), scope.ON)
            if timerTimedOut and 'onNagTimer' in dir(custom):
                self.log.debug('Calling custom onNagTimer function')
                custom.onNagTimer(self, nagSensors)
        return nagSensors

    def countOpenSections(self):
        '''
        A sensor has changed its state. We are here to calculate how many open
        sensors there are in the zone at this very moment. Saves the result in
        self.openSections and returns it. WE DO NOT INCLUDE MOTION DETECTORS
        IN THE COUNT UNLESS ARMED AWAY! E.G. Those sensors that belongs to
        group 'G_Motion'
        '''
        self.openSections = 0
        for sensor in self.sensors:
            #self.log.debug(u"Checking sensor: {} : {}".format(sensor.name.decode('utf8'), sensor.isEnabled() and sensor.isActive()))
            if sensor.isEnabled() and sensor.isActive() \
            and ('G_Motion' not in scope.itemRegistry.getItem(sensor.name).groupNames or self.getArmingMode() in [ARMINGMODE['ARMED_AWAY']]):
                self.openSections += 1
                self.log.debug(u"Open sensor: {}".format(sensor.name.decode('utf8')))
        self.log.debug(u"Number of open sections in {} is: {}".format(self.name.decode('utf8'), self.openSections))
        postUpdateCheckFirst("Z{}_Open_Sections".format(self.zoneNumber), self.openSections)
        return self.openSections

    def onSensorChange(self, sensor):
        '''
        Called whenever an enabled sensor has tripped ON or OPEN
        '''
        if self.getArmingMode() not in [ARMINGMODE['ARMED_HOME'], ARMINGMODE['ARMED_AWAY']] \
        or self.getZoneStatus() not in [ZONESTATUS['NORMAL']] \
        or (self.getArmingMode() == ARMINGMODE['ARMED_HOME'] and sensor.sensorClass == 'B') \
        or getItemValue("Z{}_Exit_Timer".format(self.zoneNumber), scope.OFF) == scope.ON:
            self.log.info(u"{} was tripped, but we are ignoring it".format(sensor.name.decode('utf8')))
            return

        self.setZoneStatus(ZONESTATUS['TRIPPED'])
        self.log.info(u"{} was tripped, starting entry timer".format(sensor.name.decode('utf8')))
        postUpdateCheckFirst("Z{}_Entry_Timer".format(self.zoneNumber), scope.ON)

class IdeAlarm(object):
    '''
    Provides ideAlarm Home Alarm System functions to openHAB
    '''

    def __init__(self):
        '''
        Initialise the IdeAlarm class

        Expects:
         - Nothing really...
        '''
        self.__version__ = '4.0.0'
        self.__version_info__ = tuple([ int(num) for num in self.__version__.split('.')])
        self.log = logging.getLogger("{}.IdeAlarm V{}".format(LOG_PREFIX, self.__version__))
        from configuration import idealarm as _cfg

        self.alarmTestMode = _cfg['ALARM_TEST_MODE']
        self.loggingLevel = _cfg['LOGGING_LEVEL']
        self.log.setLevel(self.loggingLevel)
        self.log.debug('ideAlarm configuration was reloaded')
        self.nagIntervalMinutes = _cfg['NAG_INTERVAL_MINUTES']
        self.timeCreated = DateTime.now()

        self.alarmZones = []
        for i in range(len(_cfg['ALARM_ZONES'])):
            zoneNumber = i+1
            self.alarmZones.append(IdeAlarmZone(self, zoneNumber, _cfg['ALARM_ZONES'][i]))

        for alarmZone in self.alarmZones:
            alarmZone.getNagSensors()

        self.log.info("ideAlarm object initialized with {} zones at {}".format(len(self.alarmZones), format_date(self.timeCreated, customDateTimeFormats['dateTime'])))

    def getZoneIndex(self, zoneName):
        for i in range(len(self.alarmZones)):
            if self.alarmZones[i].name == zoneName:
                return i
                self.log.debug(zoneIndex)
        self.log.warn(u"There is no alarm zone named: [{}]".format(zoneName.decode('utf8')))

    def __version__(self):
        return self.__version__

    def logVersion(self):
        self.log.info("ideAlarm Version is {}".format(self.__version__))

    def isArmed(self, zone='1'):
        '''
        zone can be the ordinal number of the alarm zone or the zone name
        '''
        zoneIndex = None
        if (str(zone).isdigit()):
            zoneIndex = int(zone) - 1
        else:
            zoneIndex = self.getZoneIndex(zone)
        return self.alarmZones[zoneIndex].isArmed()

    def isDisArmed(self, zone='1'):
        '''
        zone can be the ordinal number of the alarm zone or the zone name
        '''
        zoneIndex = None
        if (str(zone).isdigit()):
            zoneIndex = int(zone) - 1
        else:
            zoneIndex = self.getZoneIndex(zone)
        return self.alarmZones[zoneIndex].isDisArmed()

    def getZoneStatus(self, zone='1'):
        '''
        zone can be the ordinal number of the alarm zone or the zone name
        '''
        zoneIndex = None
        if (str(zone).isdigit()):
            zoneIndex = int(zone) - 1
        else:
            zoneIndex = self.getZoneIndex(zone)
        return self.alarmZones[zoneIndex].getZoneStatus()

    def getSensors(self):
        '''
        Returns a Python list of all sensors in all zones.
        '''
        sensorList = []
        for i in range(len(self.alarmZones)):
            alarmZone = self.alarmZones[i] # Get the alarm zone object
            #self.log.info(u"Getting sensors for alarm zone {}".format(alarmZone.name.decode('utf8')))
            for sensor in alarmZone.sensors:
                #self.log.info(u"Sensor: {}".format(sensor.name.decode('utf8')))
                sensorList.append(sensor.name)
        return sensorList

    def getAlertingZonesCount(self):
        '''
        Returns the total number of alerting alarm zones.
        '''
        alertingZones = 0
        for i in range(len(self.alarmZones)):
            alarmZone = self.alarmZones[i] # Get the alarm zone object
            #self.log.info(u"Checking for alert status in zone {}".format(alarmZone.name.decode('utf8')))
            if self.getZoneStatus(i) == ZONESTATUS['ALERT']: alertingZones += 1
        return alertingZones

    def getTriggers(self):
        '''
        Wraps the function with core.triggers.when for all triggers that shall trigger ideAlarm.
        '''
        from core.triggers import when
        def generatedTriggers(function):
            for item in self.getSensors():
                when("Item {} changed".format(item))(function) # TODO: Check if this works for items with accented characters in the name
            for i in range(len(self.alarmZones)):
                when("Item {} changed to ON".format(self.alarmZones[i].armAwayToggleSwitch))(function)
                when("Item {} changed to ON".format(self.alarmZones[i].armHomeToggleSwitch))(function)
                when("Item Z{}_Entry_Timer received command OFF".format(i + 1))(function)
                when("Item Z{}_Exit_Timer received command OFF".format(i + 1))(function)
                when("Item Z{}_Nag_Timer received command OFF".format(i + 1))(function)
                when("Item Z{}_Alert_Max_Timer received command OFF".format(i + 1))(function)
            return function
        return generatedTriggers

    def execute(self, event):
        '''
        Main function called whenever an item has triggered
        '''

        # Why are we here? What caused this script to trigger?
        # Is it a change of status, armingMode toggleSwitch or is it a sensor?

        for i in range(len(self.alarmZones)):
            alarmZone = self.alarmZones[i]
            if event.itemName in [alarmZone.armAwayToggleSwitch, alarmZone.armHomeToggleSwitch]:
                alarmZone.onToggleSwitch(event.itemName)
                break
            elif event.itemName == "Z{}_Entry_Timer".format(i+1):
                alarmZone.onEntryTimer() # TODO: Figure out if we only should handle event.isCommand and skip event.isUpdate (Cancelled timer)
                break
            elif event.itemName == "Z{}_Exit_Timer".format(i+1):
                alarmZone.onExitTimer()
                break
            elif event.itemName == "Z{}_Nag_Timer".format(i+1):
                alarmZone.getNagSensors(True)
                break
            elif event.itemName == "Z{}_Alert_Max_Timer".format(i+1):
                result = alarmZone.onAlertMaxTimer()
                break
            else:
                for sensor in alarmZone.sensors:
                    if event.itemName == sensor.name:
                        if sensor.isEnabled():
                            # The sensor object carries its own status.
                            # However, this is an alarm system. At this point we are not so
                            # interested in the sensors current state because it might have changed
                            # since this event triggered. We need to act upon the triggered state.
                            if isActive(scope.itemRegistry.getItem(event.itemName)):
                                alarmZone.onSensorChange(sensor) # Only active states are of interest here
                            alarmZone.getNagSensors()
                            alarmZone.countOpenSections() # updates the zone's open sections property.
                        break

ideAlarm = IdeAlarm()
