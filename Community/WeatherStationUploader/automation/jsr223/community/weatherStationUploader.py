'''
This is a community script distributed together with with Jython scripting for openHAB 2.x
https://github.com/OH-Jython-Scripters/openhab2-jython

To run, this script should be placed into the automation\jsr223\community folder. Even better
is to create a symbolic link from automation\jsr223\community\weatherStationUploader.py
to Community\WeatherStationUploader\automation\jsr223\community\weatherStationUploader.py 

You will also need to insert the example configuration entries found in
Community\WeatherStationUploader\automation\lib\python\configuration.py.example into your
openHab2-jython configuration file e.g. automation\lib\python\configuration.py
After doing that, edit the configuration data to suit your needs.

This script is dependent of an external library named meteocalc.
To install and use meteocalc, please have a look at : https://pypi.org/project/meteocalc/

Example installation command:
sudo pip install meteocalc && sudo ln -s /usr/local/lib/python2.7/dist-packages/meteocalc meteocalc
Edit classutils.py, change line 5 to: PYTHON2 = 2#sys.version_info.major
You should also add the directory /usr/local/lib/python2.7/dist-packages to the -Dpython.path in the EXTRA_JAVA_OPTS environment variable
typically found in /etc/default/openhab2 or if you have made a manual OH installation it can be set in /opt/openhab2/start.sh
'''

__version__ = '4.0.0'
__version_info__ = tuple([ int(num) for num in __version__.split('.')])

import os, time, math
from meteocalc import Temp, dew_point, heat_index
from org.joda.time import DateTime, DateTimeZone
from org.joda.time.format import DateTimeFormat
from core.date import format_date
from core.rules import rule
from core.triggers import when
from core.utils import getItemValue, getLastUpdate
from configuration import weatherStationUploader_configuration, customDateTimeFormats

wu_second_count = 10 # Loop counter

reload(configuration) # This will reload the config file when this file is saved.

WU_URL = "http://weatherstation.wunderground.com/weatherstation/updateweatherstation.php"

def ms_to_mph(input_speed):
    # convert input_speed from meter per second to miles per hour
    return round(input_speed / 0.44704, 2)

def mm_to_inch(mm):
    # convert mm to inches
    return round(mm / 25.4, 2)

def mbar_to_inches_mercury(input_pressure):
    # convert mbar to inches mercury
    return round(input_pressure * 0.02953, 3)

def lux_to_watts_m2(lux):
    # Convert lux [lx] to watt/m² (at 555 nm)
    # Should typically be around 800-900 watt/m² at mid summer full sun diation at 13.00 h
    # return int(round(float(lux) * 0.01464128843))
    return int(round(float(lux) * 0.015454545))

def getTheSensor(lbl, never_assume_dead=False, getHighest=False, getLowest=False):
    # Each sensor entry in the configuration file can be a a single item name or a python list where you can
    # define multiple sensor names. The first sensor in that list that has reported within the value set in
    # sensor_dead_after_mins will be used. (Unless never_assume_dead is set to True)
    # When "getHighest" argument is set to True, the sensor name with the highest value is picked.
    # When "getlowest" argument is set to True, the sensor name with the lowest value is picked.

    sensor_dead_after_mins = weatherStationUploader_configuration['sensor_dead_after_mins'] # The time after which a sensor is presumed to be dead

    def isSensorAlive(sName):
        if getLastUpdate(ir.getItem(sName)).isAfter(DateTime.now().minusMinutes(sensor_dead_after_mins)):
            return True
        else:
            weatherStationUploader.log.warn("Sensor device {} has not reported since: {}".format(sName, format_date(getLastUpdate(ir.getItem(sName)), customDateTimeFormats['dateTime'])))
            return False

    sensorName = None
    if lbl in weatherStationUploader_configuration['sensors'] and weatherStationUploader_configuration['sensors'][lbl] is not None:
        tSens = weatherStationUploader_configuration['sensors'][lbl]
        if isinstance(tSens, list):
            _highestValue = 0
            _lowestValue = 999999999
            for s in tSens:
                if s is None:
                    break
                # Get the first sensor that is not dead and find the sensor with the highest or the lowest value if requested
                if never_assume_dead or isSensorAlive(s):
                    if getHighest:
                        _itemValue = getItemValue(s, 0)
                        if _itemValue > _highestValue:
                            _highestValue = _itemValue
                            sensorName = s
                    elif getLowest:
                        _itemValue = getItemValue(s, 0)
                        if _itemValue < _lowestValue:
                            _lowestValue = _itemValue
                            sensorName = s
                    else:
                        sensorName = s
                        break
        else:
            if never_assume_dead or isSensorAlive(tSens):
                sensorName = tSens

    if sensorName is not None:
        weatherStationUploader.log.debug("Device used for {}: {}".format(lbl, sensorName))
    return sensorName

@rule("Weather station uploader")
@when("Time cron 0/10 * * * * ?")
def weatherStationUploader(event):
    weatherStationUploader.log.setLevel(weatherStationUploader_configuration['logLevel'])
    global wu_second_count
    if (not weatherStationUploader_configuration['stationdata']['weather_upload']) \
    or (weatherStationUploader_configuration['stationdata']['weather_upload'] and wu_second_count%weatherStationUploader_configuration['stationdata']['upload_frequency_seconds'] == 0):
        if weatherStationUploader_configuration['stationdata']['weather_upload']:
            weatherStationUploader.log.debug('Uploading data to Weather Underground')
        else:
            weatherStationUploader.log.debug('No data to will be upladed to Weather Underground')

        sdf = DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss")
        dateutc = sdf.print(DateTime.now((DateTimeZone.UTC)))

        tempf = None
        temp = None
        sensorName = getTheSensor('tempc', getLowest=True)
        if sensorName is not None:
            temp = Temp(getItemValue(sensorName, 0.0), 'c') # Outdoor temp, c - celsius, f - fahrenheit, k - kelvin
            tempf = str(round(temp.f, 1))

        soiltempf = None
        sensorName = getTheSensor('soiltempc')
        if sensorName is not None:
            _temp = Temp(getItemValue(sensorName, 0.0), 'c') # Soil temp, c - celsius, f - fahrenheit, k - kelvin
            soiltempf = str(round(_temp.f, 1))

        humidity = None
        sensorName = getTheSensor('humidity')
        if sensorName is not None:
            humidity = getItemValue(sensorName, 0.0)

        dewptf = None
        heatidxf = None
        if humidity is not None and temp is not None:
            dewptf = str(round(dew_point(temperature=temp, humidity=humidity).f, 1)) # calculate Dew Point
            heatidxf = str(round(heat_index(temperature=temp, humidity=humidity).f, 1)) # calculate Heat Index

        pressure = None
        sensorName = getTheSensor('pressurembar')
        if sensorName is not None:
            _mbar = getItemValue(sensorName, 0)
            if ((_mbar < 1070) and (_mbar > 920)): 
                pressure = str(mbar_to_inches_mercury(_mbar))

        rainin = None
        sensorName = getTheSensor('rainhour', never_assume_dead=True)
        if sensorName is not None:
            rainin = str(mm_to_inch(getItemValue(sensorName, 0.0)))

        dailyrainin = None
        sensorName = getTheSensor('raintoday', never_assume_dead=True)
        if sensorName is not None:
            dailyrainin = str(mm_to_inch(getItemValue(sensorName, 0.0)))

        soilmoisture = None
        sensorName = getTheSensor('soilmoisture')
        if sensorName is not None:
            soilmoisture = str(int(round(getItemValue(sensorName, 0.0) * 100 / 1023)))

        winddir = None
        sensorName = getTheSensor('winddir')
        if sensorName is not None:
            winddir = str(getItemValue(sensorName, 0))

        windspeedmph = None
        sensorName = getTheSensor('windspeedms')
        if sensorName is not None:
            windspeedmph = str(ms_to_mph(getItemValue(sensorName, 0.0)))

        windgustmph = None
        sensorName = getTheSensor('windgustms')
        if sensorName is not None:
            windgustmph = str(ms_to_mph(getItemValue(sensorName, 0.0)))

        windgustdir = None
        sensorName = getTheSensor('windgustdir')
        if sensorName is not None:
            windgustdir = str(getItemValue(sensorName, 0))

        windspdmph_avg2m = None
        sensorName = getTheSensor('windspeedms_avg2m')
        if sensorName is not None:
            windspdmph_avg2m = str(ms_to_mph(getItemValue(sensorName, 0.0)))

        winddir_avg2m = None
        sensorName = getTheSensor('winddir_avg2m')
        if sensorName is not None:
            winddir_avg2m = str(getItemValue(sensorName, 0))

        windgustmph_10m = None
        sensorName = getTheSensor('windgustms_10m')
        if sensorName is not None:
            windgustmph_10m = str(ms_to_mph(getItemValue(sensorName, 0.0)))

        windgustdir_10m = None
        sensorName = getTheSensor('windgustdir_10m')
        if sensorName is not None:
            windgustdir_10m = str(getItemValue(sensorName, 0))

        solarradiation = None
        sensorName = getTheSensor('solarradiation', getHighest=True)
        if sensorName is not None:
            solarradiation = str(lux_to_watts_m2(getItemValue(sensorName, 0)))

        # From http://wiki.wunderground.com/index.php/PWS_-_Upload_Protocol

        cmd = 'curl -s -G "' + WU_URL + '" ' \
            + '--data-urlencode "action=updateraw" ' \
            + ('--data-urlencode "realtime=1" ' if weatherStationUploader_configuration['stationdata']['rapid_fire_mode'] else '') \
            + ('--data-urlencode "rtfreq='+str(weatherStationUploader_configuration['stationdata']['upload_frequency_seconds'])+'" ' if weatherStationUploader_configuration['stationdata']['rapid_fire_mode'] else '') \
            + '--data-urlencode "ID='+weatherStationUploader_configuration['stationdata']['station_id']+'" ' \
            + '--data-urlencode "PASSWORD='+weatherStationUploader_configuration['stationdata']['station_key']+'" ' \
            + '--data-urlencode "dateutc='+dateutc+'" ' \
            + '--data-urlencode "softwaretype=openHAB" '
        weatherStationUploader.log.debug("")

        if weatherStationUploader_configuration['stationdata']['weather_upload']:
            weatherStationUploader.log.debug("Below is the weather data that we will send:")
        else:
            weatherStationUploader.log.debug("Below is the weather data that we would send (if weather_upload was enabled):")

        if tempf is not None:
            cmd += '--data-urlencode "tempf='+tempf+'" '
            weatherStationUploader.log.debug("tempf: "+tempf)
        if humidity is not None:
            cmd += '--data-urlencode "humidity='+str(humidity)+'" '
            weatherStationUploader.log.debug("humidity: "+str(humidity))
        if dewptf is not None:
            cmd += '--data-urlencode "dewptf='+dewptf+'" '
            weatherStationUploader.log.debug("dewptf: "+dewptf)
        if heatidxf is not None:
            cmd += '--data-urlencode "heatidxf='+heatidxf+'" '
            weatherStationUploader.log.debug("heatidxf: "+heatidxf)
        if soiltempf is not None:
            cmd += '--data-urlencode "soiltempf='+soiltempf+'" '
            weatherStationUploader.log.debug("soiltempf: "+soiltempf)
        if soilmoisture is not None:
            cmd += '--data-urlencode "soilmoisture='+soilmoisture+'" '
            weatherStationUploader.log.debug("soilmoisture: "+soilmoisture)
        if pressure is not None:
            cmd += '--data-urlencode "baromin='+pressure+'" '
            weatherStationUploader.log.debug("baromin: "+pressure)
        if rainin is not None:
            cmd += '--data-urlencode "rainin='+rainin+'" '
            weatherStationUploader.log.debug("rainin: "+rainin)
        if dailyrainin is not None:
            cmd += '--data-urlencode "dailyrainin='+dailyrainin+'" '
            weatherStationUploader.log.debug("dailyrainin: "+dailyrainin)
        if winddir is not None:
            cmd += '--data-urlencode "winddir='+winddir+'" '
            weatherStationUploader.log.debug("winddir: "+winddir)
        if windspeedmph is not None:
            cmd += '--data-urlencode "windspeedmph='+windspeedmph+'" '
            weatherStationUploader.log.debug("windspeedmph: "+windspeedmph)
        if windgustmph is not None:
            cmd += '--data-urlencode "windgustmph='+windgustmph+'" '
            weatherStationUploader.log.debug("windgustmph: "+windgustmph)
        if windgustdir is not None:
            cmd += '--data-urlencode "windgustdir='+windgustdir+'" '
            weatherStationUploader.log.debug("windgustdir: "+windgustdir)
        if windspdmph_avg2m is not None:
            cmd += '--data-urlencode "windspdmph_avg2m='+windspdmph_avg2m+'" '
            weatherStationUploader.log.debug("windspdmph_avg2m: "+windspdmph_avg2m)
        if winddir_avg2m is not None:
            cmd += '--data-urlencode "winddir_avg2m='+winddir_avg2m+'" '
            weatherStationUploader.log.debug("winddir_avg2m: "+winddir_avg2m)
        if windgustmph_10m is not None:
            cmd += '--data-urlencode "windgustmph_10m='+windgustmph_10m+'" '
            weatherStationUploader.log.debug("windgustmph_10m: "+windgustmph_10m)
        if windgustdir_10m is not None:
            cmd += '--data-urlencode "windgustdir_10m='+windgustdir_10m+'" '
            weatherStationUploader.log.debug("windgustdir_10m: "+windgustdir_10m)
        if solarradiation is not None:
            cmd += '--data-urlencode "solarradiation='+solarradiation+'" '
            weatherStationUploader.log.debug("solarradiation: "+solarradiation)
        cmd += ' 1>/dev/null 2>&1 &'
        weatherStationUploader.log.debug("")

        if weatherStationUploader_configuration['stationdata']['weather_upload']:
            weatherStationUploader.log.debug("WeatherUpload version {}, performing an upload. (second count is: {})".format(__version__, wu_second_count))
            weatherStationUploader.log.debug("cmd: {}".format(cmd))
            os.system(cmd)
    else:
        weatherStationUploader.log.debug("WeatherUpload version {}, skipping upload. (second count is: {})".format(__version__, wu_second_count))

    if (wu_second_count%weatherStationUploader_configuration['stationdata']['upload_frequency_seconds'] == 0):
        wu_second_count = 0
    wu_second_count = wu_second_count + 10 # Corresponding to CronTrigger(EVERY_10_SECONDS)
