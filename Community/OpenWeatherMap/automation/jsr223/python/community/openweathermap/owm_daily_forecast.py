# pylint: disable=invalid-name
"""
Purpose
=======

This rule will create and link the ~700 Items and groups needed to get daily
forecasts from the OWM binding using a free API key. It will also install the
Scale transformation service, if it is not already installed. There is also a
function that was used for testing purposes, which can be used to remove all
the Items and groups. As the day progresses, there will be fewer hourly
forecasts included in the gForecast_1 group.

You may want to comment out several groups and Items that you do not plan on
using, but the Forecast_Timestamp Items are required for the script to function. The
rule will also run when the script file is saved, or OH is restarted, so that
you don't have to wait for the trigger for the Item states to be populated.

The rule will arrange Items into the following group structure for days(X) 1-5.
gForecast_1 contains the forecast Items for the rest of the current day and
the current Items, since at some time there won't be any more forecasts left in
the day. The other groups contain Items for subsequent days. The rule is set
to trigger every time the binding pulls in new values.

Group labels will be updated to reflect the name of the day, and Item labels
will be updated to show the time of the forecast, based on the time provided in
the Forecast_Timestamp_XX Item.

.. code-block:: text

    gWeather
        gOpenWeatherMap
            gCurrent
            gForecast_X
                gForecast_Temperature_X
                gForecast_Pressure_X
                gForecast_Humidity_X
                gForecast_WindSpeed_X
                gForecast_WindDirection_X
                gForecast_Cloudiness_X
                gForecast_RainVolume_X
                gForecast_SnowVolume_X


Upgrading the Script
====================

When upgrading this script, remove the comment from the line containing
``remove_owm_items()``, so that all of the Items and Groups can be recreated
using the updated definitions. If you do not do this, erros are likely to
occur. In previous versions of the helper libraries, Items created using the
libraries were not persisted after an OH restart. This has now been corrected.
It is always best to upgrade the libraries and community scripts at the same
time.


Requires
========

* OpenWeatherMap binding
* OpenWeatherMap Account Thing, configured with a free API key
* OpenWeatherMap Weather and Forecast Thing, configured with 'Number of Hours'
  set to 120 and 'Number of Days' set to 0. The hours could be less (this is
  maxed out for a free API key), but you'll need to adjust the script.
* All OWM Items should be removed before using rule
* The SCALE & MAP transformation service is required, but it will be installed for
  you. If you manually editted the 'transformation' line in addons.cfg, be
  sure to add it there, or it will uninstall next OH update or cache clearing.


Known Issues
============

* ArithmeticGroupFunction.Avg does not properly average angles. An ESH issue
  has been opened for this... https://github.com/eclipse/smarthome/issues/6792.
  I noticed the units for the Cloudiness and Humidity groups display as 'one',
  but the Items display properly as '%'.


Change Log
==========

* 26/11/20: Localized Item labels
* 01/11/19: Corrected an issue where the Items were not linking.
* 01/12/19: Removed Forecast_Temperature_X, and added
  Forecast_Temperature_High_X and Forecast_Temperature_Low_X
* 01/16/19: Restructured how the rule is created
* 01/16/19: Fixed SCALE transformation install
* 01/16/19: Fixed Item existence check
* 01/16/19: Changed to using values of Timestamp Items for calculating the
  number of remaining forecasts, and the Item label times
* 01/16/19: Added group label changes to reflect current day of week
* 01/16/19: Changed Item label to use time from Timestamp Items
* 01/16/19: Added IconID
* 01/16/19: Added manual group aggregation for Condition, ConditionID, Icon,
  IconID, and WindDirection
* 01/18/19: Fixed issue with Items not being added to groups properly
* 01/18/19: Added a NULL check when manually setting group aggregation values
* 01/20/19: Fixed improper log entry after SCALE transform has been installed
* 02/04/19: Added check to make sure a Thing with ThingUID
  'openweathermap:forecast-and-weather' exists and is ONLINE
* 02/06/19: Added verification that the forecastHours and forecastDays are
  configured properly in the Thing
* 05/31/19: Fixed Cloudiness and Humidity units and group function (no more
  unit of 'one'!)
* 05/29/20: Pylint updates
* -6/14/20: Only check for SCALE transformation service if using Linux OS
* 06/14/20: Using System properties for HTTP/HTTPS ports, rather than hard coded 8080/8443
"""
from __future__ import unicode_literals
from core.log import logging, LOG_PREFIX, log_traceback
from core.actions import Transformation
import locale

ROOT_LOG = logging.getLogger("{}.owm_daily_forecast".format(LOG_PREFIX))

@log_traceback
def remove_owm_items():
    remove_owm_items.log = logging.getLogger("{}.remove_owm_items".format(LOG_PREFIX))
    from core.items import remove_item

    for item in itemRegistry.getItemsByTag("OpenWeatherMap"):
        #remove_owm_items.log.debug("'{}'".format(item))
        remove_item(item)

    # use this as a last resort, but make sure it's not removing any Items not
    # created by this script
    # for item in itemRegistry.getAll():
    #     if "Forecast_" in item.name or "Current_" in item.name:
    #         #remove_owm_items.log.debug("'{}'".format(item))
    #         remove_item(item)


#remove_owm_items()

label_value_formats = {
    "TIMESTAMP": "[%1$tY-%1$tm-%1$td %1$tI:%1$tM%1$tp]",
    "CONDITION": "[%s]",
    "CONDITION_ID": "[%s]",
    "ICON": "",
    "ICON_ID": "[%s]",
    "TEMPERATURE": "[%.0f %unit%]",
    "TEMPERATURE_HIGH": "[%.0f %unit%]",
    "TEMPERATURE_LOW": "[%.0f %unit%]",
    "PRESSURE": "[%.1f %unit%]",
    "HUMIDITY": "[%d %%]",
    "WIND_SPEED": "[%.0f %unit%]",
    "GUST_SPEED": "[%.0f %unit%]",
    "WIND_DIRECTION": "[SCALE(windDirection.scale):%s]",
    "CLOUDINESS": "[%d %%]",
    "RAIN_VOLUME": "[%.1f %unit%]",
    "SNOW_VOLUME": "[%.1f %unit%]"
}

@log_traceback
def build_label(prefix, category):
    if category in label_value_formats:
        return "{}: {} {}".format(prefix, localize_value(category), label_value_formats[category])
    else:
        ROOT_LOG.error("{} category does not exist".format(category))
        return None

@log_traceback
def build_forecast_label(time_label, category):
    if category in label_value_formats:
        label_format = "{} ({:02d}): {} {}" if isinstance(time_label, int) else "{} ({}): {} {}"
        return label_format.format(localize_value("FORECAST"), time_label, localize_value(category), label_value_formats[category])
    else:
        ROOT_LOG.error("{} category does not exist".format(category))
        return None

@log_traceback
def current_lang():
    default_locale = locale.getdefaultlocale()[0]
    if default_locale:
        return default_locale if "_" not in default_locale else default_locale.split("_")[0]
    return "en"

@log_traceback
def map_day_of_week(index, last_reading):
    day_week_idx = "TODAY" if index == 1 else str((last_reading + index - 1) % 7)
    return localize_value(day_week_idx)

@log_traceback
def localize_value(label_key):
    return Transformation.transform("MAP", "weather-{}.map".format(current_lang()), label_key)

@log_traceback
def install_transformation_service(service_name):
    import json
    from core.actions import Exec

    INSECURE_PORT = System.getProperty("org.osgi.service.http.port")
    SECURE_PORT = System.getProperty("org.osgi.service.http.port.secure")

    service_check_result = None
    try:
        service_check_result = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET -H \"Accept: application/json\" \"http://localhost:{}/rest/extensions/transformation-{}\"".format(INSECURE_PORT), 15000, service_name)
    except:
        try:
            service_check_result = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET -H \"Accept: application/json\" \"http://localhost:{}/rest/extensions/transformation-{}\"".format(SECURE_PORT), 15000, service_name)
        except:
            add_owm_items.log.warn("{} transformation service installation failed: unable to communicate with REST API".format(service_name.capitalize()))
            return
    if service_check_result is not None:            
        service_check_result = json.loads(service_check_result).get('installed')
        if not service_check_result:
            install_service_result = None
            try:
                install_service_result = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X POST -H \"Content-Type: application/json\" -H \"Accept: application/json\" \"http://localhost:{}/rest/extensions/transformation-{}/install\"".format(INSECURE_PORT), 15000, service_name)
            except:
                try:
                    install_service_result = Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{{http_code}}\" --connect-timeout 10 -m 10 -X POST -H \"Content-Type: application/json\" -H \"Accept: application/json\" \"http://localhost:{}/rest/extensions/transformation-{}/install\"".format(SECURE_PORT), 15000, service_name)
                except:
                    add_owm_items.log.warn("{} transformation service installation failed".format(service_name.capitalize()))
                    return
            if install_service_result != "200":
                add_owm_items.log.warn("{} transformation service installation failed: result {}".format(service_name.capitalize(), install_service_result))
                return
            else:
                add_owm_items.log.debug("{} transformation service has been installed".format(service_name.capitalize()))
        else:
            add_owm_items.log.debug("{} transformation service is already installed".format(service_name.capitalize()))
    else:
        add_owm_items.log.warn("{} transformation service installation failed: REST API return None".format(service_name.capitalize()))
        return

def scriptLoaded(script):
    add_owm_items()

def add_owm_items():
    add_owm_items.log = logging.getLogger("{}.add_owm_items".format(LOG_PREFIX))

    # create OWM Items and groups, if they do not exist
    scriptExtension.importPreset("RuleSupport")

    from javax.measure.quantity import Dimensionless, Temperature, Length, Speed, Pressure#, Angle

    try:
        from org.openhab.core.thing import ThingTypeUID
        from org.openhab.core.thing import ChannelUID
    except:
        from org.eclipse.smarthome.core.thing import ThingTypeUID
        from org.eclipse.smarthome.core.thing import ChannelUID

    try:
        from org.eclipse.smarthome.core.library.types import QuantityTypeArithmeticGroupFunction
    except:
        from org.openhab.core.library.types import QuantityTypeArithmeticGroupFunction

    from core.items import add_item
    from core.links import add_link

    try:
        owm_thing_uid = None
        for thing in things.getAll():
            if thing.getThingTypeUID() == ThingTypeUID("openweathermap:weather-and-forecast"):
                if str(thing.statusInfo) == "ONLINE":
                    thing_configuration = thing.getConfiguration()
                    forecast_hours = thing_configuration.get("forecastHours")
                    if str(forecast_hours) == "120":
                        forecast_days = thing_configuration.get("forecastDays")
                        if str(forecast_days) == "0":
                            owm_thing_uid = str(thing.getUID())
                            break
                        else:
                            add_owm_items.log.warn("Thing found, but forecastDays is not set to [0]: forecastDays='{}'".format(forecast_days))
                    else:
                        add_owm_items.log.warn("Thing found, but forecast_hours is not set to [120]: forecastHours='{}'".format(forecast_hours))
                else:
                    add_owm_items.log.warn("Thing found, but statusInfo was not [ONLINE]: statusInfo='{}'".format(thing.statusInfo))
        if owm_thing_uid is None:
            add_owm_items.log.warn("No Thing found with ThingTypeUID 'openweathermap:weather-and-forecast', or it was not ONLINE, or it was improperly configured for the free API. Exiting script.")
        else:
            add_owm_items.log.debug("owm_thing_uid set to '{}'".format(owm_thing_uid))

            # install Scale & MAP transformation serviceS, if not already installed
            from java.lang import System

            if System.getProperty("os.name") == "Linux":
                install_transformation_service("scale")
                install_transformation_service("map")

            # create Current group and Items
            current_label = localize_value("CURRENT")

            if itemRegistry.getItems("gOpenWeatherMap") == []:
                add_item("gOpenWeatherMap", item_type="Group", groups=["gWeather"], label="OpenWeatherMap", tags=["OpenWeatherMap"])
            if itemRegistry.getItems("gCurrent") == []:
                add_item("gCurrent", item_type="Group", groups=["gOpenWeatherMap"], label=current_label, tags=["OpenWeatherMap"])
            if itemRegistry.getItems("Current_Timestamp") == []:
                add_item("Current_Timestamp", item_type="DateTime", groups=["gCurrent", "gForecast_Timestamp_1"], label=build_label(current_label, "TIMESTAMP"), category="Time", tags=["OpenWeatherMap"])
                add_link("Current_Timestamp", ChannelUID(owm_thing_uid + ":current#time-stamp"))
            if itemRegistry.getItems("Current_Condition") == []:
                add_item("Current_Condition", item_type="String", groups=["gCurrent", "gForecast_Condition_1"], label=build_label(current_label,"CONDITION"), category="Sun_Clouds", tags=["OpenWeatherMap"])
                add_link("Current_Condition", ChannelUID(owm_thing_uid + ":current#condition"))
            if itemRegistry.getItems("Current_ConditionID") == []:
                add_item("Current_ConditionID", item_type="String", groups=["gCurrent", "gForecast_ConditionID_1"], label=build_label(current_label,"CONDITION_ID"), tags=["OpenWeatherMap"])
                add_link("Current_ConditionID", ChannelUID(owm_thing_uid + ":current#condition-id"))
            if itemRegistry.getItems("Current_IconID") == []:
                add_item("Current_IconID", item_type="String", groups=["gCurrent", "gForecast_IconID_1"], label=build_label(current_label,"ICON_ID"), tags=["OpenWeatherMap"])
                add_link("Current_IconID", ChannelUID(owm_thing_uid + ":current#icon-id"))
            if itemRegistry.getItems("Current_Icon") == []:
                add_item("Current_Icon", item_type="Image", groups=["gCurrent", "gForecast_Icon_1"], label=build_label(current_label,"ICON"), tags=["OpenWeatherMap"])
                add_link("Current_Icon", ChannelUID(owm_thing_uid + ":current#icon"))
            if itemRegistry.getItems("Current_Temperature") == []:
                add_item("Current_Temperature", item_type="Number:Temperature", groups=["gCurrent", "gForecast_Temperature_High_1", "gForecast_Temperature_Low_1"], label=build_label(current_label,"TEMPERATURE"), category="Temperature", tags=["OpenWeatherMap"])
                add_link("Current_Temperature", ChannelUID(owm_thing_uid + ":current#temperature"))
            if itemRegistry.getItems("Current_Pressure") == []:
                add_item("Current_Pressure", item_type="Number:Pressure", groups=["gCurrent", "gForecast_Pressure_1"], label=build_label(current_label,"PRESSURE"), category="Pressure", tags=["OpenWeatherMap"])
                add_link("Current_Pressure", ChannelUID(owm_thing_uid + ":current#pressure"))
            if itemRegistry.getItems("Current_Humidity") == []:
                add_item("Current_Humidity", item_type="Number:Dimensionless", groups=["gCurrent", "gForecast_Humidity_1"], label=build_label(current_label,"HUMIDITY"), category="Humidity", tags=["OpenWeatherMap"])
                add_link("Current_Humidity", ChannelUID(owm_thing_uid + ":current#humidity"))
            if itemRegistry.getItems("Current_WindSpeed") == []:
                add_item("Current_WindSpeed", item_type="Number:Speed", groups=["gCurrent", "gForecast_WindSpeed_1"], label=build_label(current_label,"WIND_SPEED"), category="Wind", tags=["OpenWeatherMap"])
                add_link("Current_WindSpeed", ChannelUID(owm_thing_uid + ":current#wind-speed"))
            if itemRegistry.getItems("Current_GustSpeed") == []:
                add_item("Current_GustSpeed", item_type="Number:Speed", groups=["gCurrent", "gForecast_GustSpeed_1"], label=build_label(current_label,"GUST_SPEED"), category="Wind", tags=["OpenWeatherMap"])
                add_link("Current_GustSpeed", ChannelUID(owm_thing_uid + ":current#gust-speed"))
            if itemRegistry.getItems("Current_WindDirection") == []:
                add_item("Current_WindDirection", item_type="Number:Angle", groups=["gCurrent", "gForecast_WindDirection_1"], label=build_label(current_label,"WIND_DIRECTION"), category="Wind", tags=["OpenWeatherMap"])
                add_link("Current_WindDirection", ChannelUID(owm_thing_uid + ":current#wind-direction"))
            if itemRegistry.getItems("Current_Cloudiness") == []:
                add_item("Current_Cloudiness", item_type="Number:Dimensionless", groups=["gCurrent", "gForecast_Cloudiness_1"], label=build_label(current_label,"CLOUDINESS"), category="Sun_Clouds", tags=["OpenWeatherMap"])
                add_link("Current_Cloudiness", ChannelUID(owm_thing_uid + ":current#cloudiness"))
            if itemRegistry.getItems("Current_RainVolume") == []:
                add_item("Current_RainVolume", item_type="Number:Length", groups=["gCurrent", "gForecast_RainVolume_1"], label=build_label(current_label,"RAIN_VOLUME"), category="Rain", tags=["OpenWeatherMap"])
                add_link("Current_RainVolume", ChannelUID(owm_thing_uid + ":current#rain"))
            if itemRegistry.getItems("Current_SnowVolume") == []:
                add_item("Current_SnowVolume", item_type="Number:Length", groups=["gCurrent", "gForecast_SnowVolume_1"], label=build_label(current_label,"SNOW_VOLUME"), category="Snow", tags=["OpenWeatherMap"])
                add_link("Current_SnowVolume", ChannelUID(owm_thing_uid + ":current#snow"))

            # create Forecast groups
            from org.joda.time import DateTime
            last_reading = DateTime(str(items["Current_Timestamp"])).getDayOfWeek() - 1
            for index in range(1, 6):
                day_of_the_week = map_day_of_week(index, last_reading)
                
                if itemRegistry.getItems("gForecast_" + str(index)) == []:
                    add_item("gForecast_" + str(index), item_type="Group", groups=["gOpenWeatherMap"], label=day_of_the_week, tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Timestamp_" + str(index)) == []:
                    add_item("gForecast_Timestamp_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"TIMESTAMP"), category="Time", tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Condition_" + str(index)) == []:
                    add_item("gForecast_Condition_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"CONDITION"), gi_base_type="String", category="Sun_Clouds", tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_ConditionID_" + str(index)) == []:
                    add_item("gForecast_ConditionID_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"CONDITION_ID"), gi_base_type="String", tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_IconID_" + str(index)) == []:
                    add_item("gForecast_IconID_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"ICON_ID"), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Icon_" + str(index)) == []:
                    add_item("gForecast_Icon_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"ICON"), gi_base_type="Image", tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Temperature_High_" + str(index)) == []:
                    add_item("gForecast_Temperature_High_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"TEMPERATURE_HIGH"), category="Temperature_Hot", gi_base_type="Number:Temperature", group_function=QuantityTypeArithmeticGroupFunction.Max(Temperature), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Temperature_Low_" + str(index)) == []:
                    add_item("gForecast_Temperature_Low_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"TEMPERATURE_LOW"), category="Temperature_Cold", gi_base_type="Number:Temperature", group_function=QuantityTypeArithmeticGroupFunction.Min(Temperature), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Pressure_" + str(index)) == []:
                    add_item("gForecast_Pressure_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"PRESSURE"), category="Pressure", gi_base_type="Number:Pressure", group_function=QuantityTypeArithmeticGroupFunction.Max(Pressure), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Humidity_" + str(index)) == []:
                    add_item("gForecast_Humidity_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"HUMIDITY"), category="Humidity", gi_base_type="Number:Dimensionless", group_function=QuantityTypeArithmeticGroupFunction.Max(Dimensionless), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_WindSpeed_" + str(index)) == []:
                    add_item("gForecast_WindSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"WIND_SPEED"), category="Wind", gi_base_type="Number:Speed", group_function=QuantityTypeArithmeticGroupFunction.Max(Speed), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_GustSpeed_" + str(index)) == []:
                    add_item("gForecast_GustSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"GUST_SPEED"), category="Wind", gi_base_type="Number:Speed", group_function=QuantityTypeArithmeticGroupFunction.Max(Speed), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_WindDirection_" + str(index)) == []:
                    #add_item("gForecast_WindDirection_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=day_of_the_week + ": Wind direction [SCALE(windDirection.scale):%s]", category="Wind", gi_base_type="Number:Angle", group_function=QuantityTypeArithmeticGroupFunction.Avg(Angle), tags=["OpenWeatherMap"])# this doesn't work properly yet
                    add_item("gForecast_WindDirection_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"WIND_DIRECTION"), category="Wind", gi_base_type="Number:Angle", tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_Cloudiness_" + str(index)) == []:
                    add_item("gForecast_Cloudiness_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"CLOUDINESS"), category="Sun_Clouds", gi_base_type="Number:Dimensionless", group_function=QuantityTypeArithmeticGroupFunction.Max(Dimensionless), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_RainVolume_" + str(index)) == []:
                    add_item("gForecast_RainVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"RAIN_VOLUME"), category="Rain", gi_base_type="Number:Length", group_function=QuantityTypeArithmeticGroupFunction.Sum(Length), tags=["OpenWeatherMap"])
                if itemRegistry.getItems("gForecast_SnowVolume_" + str(index)) == []:
                    add_item("gForecast_SnowVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=build_label(day_of_the_week,"SNOW_VOLUME"), category="Snow", gi_base_type="Number:Length", group_function=QuantityTypeArithmeticGroupFunction.Sum(Length), tags=["OpenWeatherMap"])

            # create Forecast Items
            for index in range(1, 41):
                idx_label = index * 3
                if itemRegistry.getItems("Forecast_Timestamp_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Timestamp_{:02d}".format(idx_label), item_type="DateTime", label=build_forecast_label(idx_label, "TIMESTAMP"), category="Time", tags=["OpenWeatherMap"])
                    add_link("Forecast_Timestamp_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#time-stamp".format(idx_label)))
                if itemRegistry.getItems("Forecast_Condition_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Condition_{:02d}".format(idx_label), item_type="String", label=build_forecast_label(idx_label, "CONDITION"), category="Sun_Clouds", tags=["OpenWeatherMap"])
                    add_link("Forecast_Condition_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#condition".format(idx_label)))
                if itemRegistry.getItems("Forecast_ConditionID_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_ConditionID_{:02d}".format(idx_label), item_type="String", label=build_forecast_label(idx_label, "CONDITION_ID"), tags=["OpenWeatherMap"])
                    add_link("Forecast_ConditionID_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#condition-id".format(idx_label)))
                if itemRegistry.getItems("Forecast_IconID_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_IconID_{:02d}".format(idx_label), item_type="String", label=build_forecast_label(idx_label, "ICON_ID"), tags=["OpenWeatherMap"])
                    add_link("Forecast_IconID_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#icon-id".format(idx_label)))
                if itemRegistry.getItems("Forecast_Icon_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Icon_{:02d}".format(idx_label), item_type="Image", label=build_forecast_label(idx_label, "ICON"), tags=["OpenWeatherMap"])
                    add_link("Forecast_Icon_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#icon".format(idx_label)))
                if itemRegistry.getItems("Forecast_Temperature_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Temperature_{:02d}".format(idx_label), item_type="Number:Temperature", label=build_forecast_label(idx_label, "TEMPERATURE"), category="Temperature", tags=["OpenWeatherMap"])
                    add_link("Forecast_Temperature_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#temperature".format(idx_label)))
                if itemRegistry.getItems("Forecast_Pressure_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Pressure_{:02d}".format(idx_label), item_type="Number:Pressure", label=build_forecast_label(idx_label, "PRESSURE"), category="Pressure", tags=["OpenWeatherMap"])
                    add_link("Forecast_Pressure_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#pressure".format(idx_label)))
                if itemRegistry.getItems("Forecast_Humidity_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Humidity_{:02d}".format(idx_label), item_type="Number:Dimensionless", label=build_forecast_label(idx_label, "HUMIDITY"), category="Humidity", tags=["OpenWeatherMap"])
                    add_link("Forecast_Humidity_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#humidity".format(idx_label)))
                if itemRegistry.getItems("Forecast_WindSpeed_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_WindSpeed_{:02d}".format(idx_label), item_type="Number:Speed", label=build_forecast_label(idx_label, "WIND_SPEED"), category="Wind", tags=["OpenWeatherMap"])
                    add_link("Forecast_WindSpeed_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#wind-speed".format(idx_label)))
                if itemRegistry.getItems("Forecast_GustSpeed_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_GustSpeed_{:02d}".format(idx_label), item_type="Number:Speed", label=build_forecast_label(idx_label, "GUST_SPEED"), category="Wind", tags=["OpenWeatherMap"])
                    add_link("Forecast_GustSpeed_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#gust-speed".format(idx_label)))
                if itemRegistry.getItems("Forecast_WindDirection_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_WindDirection_{:02d}".format(idx_label), item_type="Number:Angle", label=build_forecast_label(idx_label, "WIND_DIRECTION"), category="Wind", tags=["OpenWeatherMap"])
                    add_link("Forecast_WindDirection_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#wind-direction".format(idx_label)))
                if itemRegistry.getItems("Forecast_Cloudiness_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_Cloudiness_{:02d}".format(idx_label), item_type="Number:Dimensionless", label=build_forecast_label(idx_label, "CLOUDINESS"), category="Sun_Clouds", tags=["OpenWeatherMap"])
                    add_link("Forecast_Cloudiness_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#cloudiness".format(idx_label)))
                if itemRegistry.getItems("Forecast_RainVolume_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_RainVolume_{:02d}".format(idx_label), item_type="Number:Length", label=build_forecast_label(idx_label, "RAIN_VOLUME"), category="Rain", tags=["OpenWeatherMap"])
                    add_link("Forecast_RainVolume_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#rain".format(idx_label)))
                if itemRegistry.getItems("Forecast_SnowVolume_{:02d}".format(idx_label)) == []:
                    add_item("Forecast_SnowVolume_{:02d}".format(idx_label), item_type="Number:Length", label=build_forecast_label(idx_label, "SNOW_VOLUME"), category="Snow", tags=["OpenWeatherMap"])
                    add_link("Forecast_SnowVolume_{:02d}".format(idx_label), ChannelUID(owm_thing_uid + ":forecastHours{:02d}#snow".format(idx_label)))

            from core.rules import rule
            from core.triggers import when


            @rule("Add OpenWeatherMap Items to daily forecast groups")
            @when("Item Current_Timestamp changed")
            def add_owm_items_to_groups(event):
                # remove hourly forecast Items from groups
                for group_index in range(1, 6):
                    for member in [item for item in itemRegistry.getItem("gForecast_Timestamp_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Timestamp_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Condition_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Condition_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_ConditionID_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_ConditionID_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_IconID_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_IconID_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Icon_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Icon_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Temperature_High_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Temperature_High_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Temperature_Low_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Temperature_Low_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Pressure_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Pressure_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Humidity_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Humidity_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_WindSpeed_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_WindSpeed_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_GustSpeed_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_GustSpeed_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_WindDirection_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_WindDirection_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_Cloudiness_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_Cloudiness_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_RainVolume_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_RainVolume_{}".format(group_index)).removeMember(member)
                    for member in [item for item in itemRegistry.getItem("gForecast_SnowVolume_{}".format(group_index)).getMembers() if "Current" not in item.name]:
                        itemRegistry.getItem("gForecast_SnowVolume_{}".format(group_index)).removeMember(member)

                # update group labels to reflect week day
                from org.joda.time import DateTime
                last_reading = DateTime(str(items["Current_Timestamp"])).getDayOfWeek() - 1
                for index in range(1, 6):
                    day_of_the_week = map_day_of_week(index, last_reading)

                    itemRegistry.getItem("gForecast_" + str(index)).setLabel(day_of_the_week)
                    itemRegistry.getItem("gForecast_Timestamp_" + str(index)).setLabel(build_label(day_of_the_week, "TIMESTAMP"))
                    itemRegistry.getItem("gForecast_Condition_" + str(index)).setLabel(build_label(day_of_the_week, "CONDITION"))
                    itemRegistry.getItem("gForecast_ConditionID_" + str(index)).setLabel(build_label(day_of_the_week, "CONDITION_ID"))
                    itemRegistry.getItem("gForecast_IconID_" + str(index)).setLabel(build_label(day_of_the_week, "ICON_ID"))
                    itemRegistry.getItem("gForecast_Icon_" + str(index)).setLabel(build_label(day_of_the_week, "ICON"))
                    itemRegistry.getItem("gForecast_Temperature_High_" + str(index)).setLabel(build_label(day_of_the_week, "TEMPERATURE_HIGH"))
                    itemRegistry.getItem("gForecast_Temperature_Low_" + str(index)).setLabel(build_label(day_of_the_week, "TEMPERATURE_LOW"))
                    itemRegistry.getItem("gForecast_Pressure_" + str(index)).setLabel(build_label(day_of_the_week, "PRESSURE"))
                    itemRegistry.getItem("gForecast_Humidity_" + str(index)).setLabel(build_label(day_of_the_week, "HUMIDITY"))
                    itemRegistry.getItem("gForecast_WindSpeed_" + str(index)).setLabel(build_label(day_of_the_week, "WIND_SPEED"))
                    itemRegistry.getItem("gForecast_GustSpeed_" + str(index)).setLabel(build_label(day_of_the_week, "GUST_SPEED"))
                    itemRegistry.getItem("gForecast_WindDirection_" + str(index)).setLabel(build_label(day_of_the_week, "WIND_DIRECTION"))
                    itemRegistry.getItem("gForecast_Cloudiness_" + str(index)).setLabel(build_label(day_of_the_week, "CLOUDINESS"))
                    itemRegistry.getItem("gForecast_RainVolume_" + str(index)).setLabel(build_label(day_of_the_week, "RAIN_VOLUME"))
                    itemRegistry.getItem("gForecast_SnowVolume_" + str(index)).setLabel(build_label(day_of_the_week, "SNOW_VOLUME"))

                # add Forecast Items to groups, and update the labels to reflect time
                group_index = 1
                for index in range(1, 41):
                    forecast_idx = 3 * index
                    if DateTime(str(items["Forecast_Timestamp_{:02}".format(forecast_idx)])).getDayOfWeek() - 1 != (DateTime.now().getDayOfWeek() + group_index - 2) % 7:
                        if group_index == 5:
                            break# we're at the end of the forecasts that fit into 5 days
                        else:
                            group_index += 1
                    time_label = items["Forecast_Timestamp_{:02}".format(forecast_idx)].format("%1$tl:%1$tM%1$tp")

                    itemRegistry.getItem("gForecast_Timestamp_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Timestamp_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Timestamp_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "TIMESTAMP"))

                    itemRegistry.getItem("gForecast_Condition_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Condition_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Condition_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "CONDITION"))

                    itemRegistry.getItem("gForecast_ConditionID_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_ConditionID_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_ConditionID_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "CONDITION_ID"))

                    itemRegistry.getItem("gForecast_IconID_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_IconID_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_IconID_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "ICON_ID"))

                    itemRegistry.getItem("gForecast_Icon_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Icon_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Icon_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "ICON"))

                    itemRegistry.getItem("gForecast_Temperature_High_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Temperature_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Temperature_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "TEMPERATURE_HIGH"))

                    itemRegistry.getItem("gForecast_Temperature_Low_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Temperature_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Temperature_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "TEMPERATURE_LOW"))

                    itemRegistry.getItem("gForecast_Pressure_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Pressure_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Pressure_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "PRESSURE"))

                    itemRegistry.getItem("gForecast_Humidity_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Humidity_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Humidity_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "HUMIDITY"))

                    itemRegistry.getItem("gForecast_WindSpeed_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_WindSpeed_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_WindSpeed_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "WIND_SPEED"))

                    itemRegistry.getItem("gForecast_GustSpeed_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_GustSpeed_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_GustSpeed_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "GUST_SPEED"))

                    itemRegistry.getItem("gForecast_WindDirection_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_WindDirection_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_WindDirection_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "WIND_DIRECTION"))

                    itemRegistry.getItem("gForecast_Cloudiness_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_Cloudiness_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_Cloudiness_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "CLOUDINESS"))

                    itemRegistry.getItem("gForecast_RainVolume_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_RainVolume_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_RainVolume_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "RAIN_VOLUME"))

                    itemRegistry.getItem("gForecast_SnowVolume_{}".format(group_index)).addMember(itemRegistry.getItem("Forecast_SnowVolume_{:02d}".format(forecast_idx)))
                    itemRegistry.getItem("Forecast_SnowVolume_{:02d}".format(forecast_idx)).setLabel(build_forecast_label(time_label, "SNOW_VOLUME"))

                # set Condition, Icon and WindDirection group values
                for index in range(1, 6):
                    for group in [600, 200, 500, 300, 700, 800]:# the Conditions are organized into groups (https://openweathermap.org/weather-conditions), which I have prioritized
                        forecast_items = [item for item in itemRegistry.getItem("gForecast_ConditionID_" + str(index)).getMembers() if int(item.state.toString()) in range(group, group + 100)]
                        if forecast_items:
                            sorted_items = sorted(forecast_items, key=lambda item: int(item.state.toString()))
                            selected_item = sorted_items.pop()# this will provide the highest value in the sorted list of Items, which is usually the most severe condition
                            events.postUpdate("gForecast_ConditionID_" + str(index), selected_item.state.toString())
                            events.postUpdate("gForecast_Condition_" + str(index), items[selected_item.name.replace("ID", "")].toString())
                            events.postUpdate("gForecast_IconID_" + str(index), items[selected_item.name.replace("Condition", "Icon")].toString())
                            events.postUpdate(itemRegistry.getItem("gForecast_Icon_" + str(index)), items[selected_item.name.replace("ConditionID", "Icon")])
                            break
                    # this can be removed when QuantityTypeArithmeticGroupFunction.Avg() is fixed for Number:Angle
                    wind_direction_item_states = [item.state.intValue() for item in itemRegistry.getItem("gForecast_WindDirection_" + str(index)).getMembers() if not isinstance(item.state, UnDefType)]
                    if wind_direction_item_states:
                        wind_direction_average = reduce(lambda x, y: (((x + y) / 2) if y - x < 180 else (x + y + 360) / 2) % 360, wind_direction_item_states)
                        events.postUpdate("gForecast_WindDirection_" + str(index), str(wind_direction_average))

                add_owm_items_to_groups.log.debug("Updated groups and Items")

            add_owm_items_to_groups(None)
    except:
        import traceback
        add_owm_items.log.error(traceback.format_exc())
