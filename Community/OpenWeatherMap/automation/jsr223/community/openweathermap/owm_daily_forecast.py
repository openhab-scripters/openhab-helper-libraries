'''
PURPOSE:
This rule will create and link the ~600 Items and groups needed to get daily
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
gForecast_1 contains the forecast Items for the rest of the current day, and
the current Items, since at some time there won't be any more forecasts left in
the day. The other groups contain Items for subsequent days. The rule is set
to trigger every time the binding pulls in new values.

Group labels will be updated to reflect the name of the day, and Item labels
will be updated to show the time of the forecast, based on the time provided in
the Forecast_Timestamp_XX Item.

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

REQUIRES:
    OpenWeatherMap binding
    OpenWeatherMap Account Thing, configured with a free API key
    OpenWeatherMap Weather and Forecast Thing, configured with
        'Number of Hours' set to 120 and 'Number of Days' set to 0. The hours
        could be less (this is maxed out for a free API key), but you'll need
        to adjust the script.
    All OWM Items should be removed before using rule
    The SCALE transformation service is required, but it will be installed for
        you. If you manually editted the 'transformation' line in addons.cfg,
        be sure to add it there, or it will uninstall next OH update or cache
        clearing.

KNOWN ISSUES:
ArithmethicGroupFunction.Avg does not properly average angles. An ESH issue has
    been opened for this... https://github.com/eclipse/smarthome/issues/6792.
I noticed the units for the Cloudiness and Humidity groups display as 'one',
    but the Items display properly as '%'.

01/11/19: Corrected an issue where the Items were not linking.
01/12/19: Removed Forecast_Temperature_X, and added Forecast_Temperature_High_X
    and Forecast_Temperature_Low_X
01/16/19: Restructured how the rule is created
01/16/19: Fixed SCALE transformation install
01/16/19: Fixed Item existence check
01/16/19: Changed to using values of Timestamp Items for calculating the number
    of remaining forecasts, and the Item label times
01/16/19: Added group label changes to reflect current day of week
01/16/19: Changed Item label to use time from Timestamp Items
01/16/19: Added IconID
01/16/19: Added manual group aggregation for Condition, ConditionID, Icon,
    IconID, and WindDirection
01/18/19: Fixed issue with Items not being added to groups properly
01/18/19: Added a NULL check when manually setting group aggregation values
01/20/19: Fixed improper log entry after SCALE transform has been installed
02/04/19: Added check to make sure a Thing with ThingUID
    'openweathermap:forecast-and-weather' exists and is ONLINE
02/06/19: Added verification that the forecastHours and forecastDays are
    configured properly in the Thing
'''
from core.log import logging, LOG_PREFIX, log_traceback

@log_traceback
def removeOWMItems():
    removeOWMItems.log = logging.getLogger(LOG_PREFIX + ".removeOWMItems")
    from core.items import remove_item

    for item in ir.getItemsByTag("OpenWeatherMap"):
        removeOWMItems.log.debug("removeOWMItems: [{}]".format(item))
        remove_item(item)
    '''
    # use this as a last resort, but make sure it's not removing any Items not created by this script
    for item in ir.getAll():
        if "Forecast_" in item.name or "Current_" in item.name:
            removeOWMItems.log.debug("removeOWMItems: [{}]".format(item))
            remove_item(item)
    '''    
#removeOWMItems()

def addOWMItems():
    addOWMItems.log = logging.getLogger(LOG_PREFIX + ".addOWMItems")

    # create OWM Items and groups, if they do not exist
    from org.eclipse.smarthome.core.thing import ThingTypeUID
    from org.eclipse.smarthome.core.thing import ChannelUID
    from org.eclipse.smarthome.config.core import Configuration
    from org.eclipse.smarthome.core.library.types import ArithmeticGroupFunction

    from core.items import add_item
    from core.links import add_link

    owmThingUID = None
    for thing in things.getAll():
        if thing.getThingTypeUID() == ThingTypeUID("openweathermap:weather-and-forecast"):
            if str(thing.statusInfo) == "ONLINE":
                thingConfiguration = thing.getConfiguration()
                forecastHours = thingConfiguration.get("forecastHours")
                if str(forecastHours) == "120":
                    forecastDays = thingConfiguration.get("forecastDays")
                    if str(forecastDays) == "0":
                        owmThingUID = str(thing.getUID())
                        break
                    else:
                        addOWMItems.log.warn("Thing found, but forecastDays is not set to [0]: forecastDays=[{}]".format(forecastDays))
                else:
                    addOWMItems.log.warn("Thing found, but forecastHours is not set to [120]: forecastHours=[{}]".format(forecastHours))
            else:
                addOWMItems.log.warn("Thing found, but statusInfo was not [ONLINE]: statusInfo=[{}]".format(thing.statusInfo))
    if owmThingUID is None:
        addOWMItems.log.warn("No Thing found with ThingTypeUID 'openweathermap:weather-and-forecast', or it was not ONLINE, or it was improperly configured for the free API. Exiting script.")
    else:
        addOWMItems.log.debug("owmThingUID set to [{}]".format(owmThingUID))

        # install Scale transformation service, if not already
        from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine
        import json

        scaleCheckResult = json.loads(executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET -H \"Accept: application/json\" \"http://localhost:8080/rest/extensions/transformation-scale\"",15000))['installed']
        if not scaleCheckResult:
            installScaleResult = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{http_code}\" --connect-timeout 10 -m 10 -X POST -H \"Content-Type: application/json\" -H \"Accept: application/json\" \"http://localhost:8080/rest/extensions/transformation-scale/install\"",15000)
            if installScaleResult != "200":
                addOWMItems.log.debug("Scale transformation service installation failed")
                return
            else:
                addOWMItems.log.debug("Scale transformation service has been installed")
        else:
            addOWMItems.log.debug("Scale transformation service is already installed")

        # create Current group and Items
        if ir.getItems("gOpenWeatherMap") == []:
            add_item("gOpenWeatherMap", item_type="Group", groups=["gWeather"], label="OpenWeatherMap", tags=["OpenWeatherMap"])
        if ir.getItems("gCurrent") == []:
            add_item("gCurrent", item_type="Group", groups=["gOpenWeatherMap"], label="Current", tags=["OpenWeatherMap"])
        if ir.getItems("Current_Timestamp") == []:
            add_item("Current_Timestamp", item_type="DateTime", groups=["gCurrent", "gForecast_Timestamp_1"], label="Current: Timestamp [%1$tY-%1$tm-%1$td %1$tI:%1$tM%1$tp]", category="Time", tags=["OpenWeatherMap"])
            add_link("Current_Timestamp", ChannelUID(owmThingUID + ":current#time-stamp"))
        if ir.getItems("Current_Condition") == []:
            add_item("Current_Condition", item_type="String", groups=["gCurrent", "gForecast_Condition_1"], label="Current: Condition [%s]", category="Sun_Clouds", tags=["OpenWeatherMap"])
            add_link("Current_Condition", ChannelUID(owmThingUID + ":current#condition"))
        if ir.getItems("Current_ConditionID") == []:
            add_item("Current_ConditionID", item_type="String", groups=["gCurrent", "gForecast_ConditionID_1"], label="Current: Condition ID [%s]", tags=["OpenWeatherMap"])
            add_link("Current_ConditionID", ChannelUID(owmThingUID + ":current#condition-id"))
        if ir.getItems("Current_IconID") == []:
            add_item("Current_IconID", item_type="String", groups=["gCurrent", "gForecast_IconID_1"], label="Current: Icon ID [%s]", tags=["OpenWeatherMap"])
            add_link("Current_IconID", ChannelUID(owmThingUID + ":current#icon-id"))
        if ir.getItems("Current_Icon") == []:
            add_item("Current_Icon", item_type="Image", groups=["gCurrent", "gForecast_Icon_1"], label="Current: Icon", tags=["OpenWeatherMap"])
            add_link("Current_Icon", ChannelUID(owmThingUID + ":current#icon"))
        if ir.getItems("Current_Temperature") == []:
            add_item("Current_Temperature", item_type="Number:Temperature", groups=["gCurrent", "gForecast_Temperature_High_1", "gForecast_Temperature_Low_1"], label="Current: Temperature [%.0f %unit%]", category="Temperature", tags=["OpenWeatherMap"])
            add_link("Current_Temperature", ChannelUID(owmThingUID + ":current#temperature"))
        if ir.getItems("Current_Pressure") == []:
            add_item("Current_Pressure", item_type="Number:Pressure", groups=["gCurrent", "gForecast_Pressure_1"], label="Current: Pressure [%.1f %unit%]", category="Pressure", tags=["OpenWeatherMap"])
            add_link("Current_Pressure", ChannelUID(owmThingUID + ":current#pressure"))
        if ir.getItems("Current_Humidity") == []:
            add_item("Current_Humidity", item_type="Number:Dimensionless", groups=["gCurrent", "gForecast_Humidity_1"], label="Current: Humidity [%d %unit%]", category="Humidity", tags=["OpenWeatherMap"])
            add_link("Current_Humidity", ChannelUID(owmThingUID + ":current#humidity"))
        if ir.getItems("Current_WindSpeed") == []:
            add_item("Current_WindSpeed", item_type="Number:Speed", groups=["gCurrent", "gForecast_WindSpeed_1"], label="Current: Wind speed [%.0f %unit%]", category="Wind", tags=["OpenWeatherMap"])
            add_link("Current_WindSpeed", ChannelUID(owmThingUID + ":current#wind-speed"))
        if ir.getItems("Current_GustSpeed") == []:
            add_item("Current_GustSpeed", item_type="Number:Speed", groups=["gCurrent", "gForecast_GustSpeed_1"], label="Current: Gust speed [%.0f %unit%]", category="Wind", tags=["OpenWeatherMap"])
            add_link("Current_GustSpeed", ChannelUID(owmThingUID + ":current#gust-speed"))
        if ir.getItems("Current_WindDirection") == []:
            add_item("Current_WindDirection", item_type="Number:Angle", groups=["gCurrent", "gForecast_WindDirection_1"], label="Current: Wind direction [SCALE(windDirection.scale):%s]", category="Wind", tags=["OpenWeatherMap"])
            add_link("Current_WindDirection", ChannelUID(owmThingUID + ":current#wind-direction"))
        if ir.getItems("Current_Cloudiness") == []:
            add_item("Current_Cloudiness", item_type="Number:Dimensionless", groups=["gCurrent", "gForecast_Cloudiness_1"], label="Current: Cloudiness [%d %unit%]", category="Sun_Clouds", tags=["OpenWeatherMap"])
            add_link("Current_Cloudiness", ChannelUID(owmThingUID + ":current#cloudiness"))
        if ir.getItems("Current_RainVolume") == []:
            add_item("Current_RainVolume", item_type="Number:Length", groups=["gCurrent", "gForecast_RainVolume_1"], label="Current: Rain volume [%.1f %unit%]", category="Rain", tags=["OpenWeatherMap"])
            add_link("Current_RainVolume", ChannelUID(owmThingUID + ":current#rain"))
        if ir.getItems("Current_SnowVolume") == []:
            add_item("Current_SnowVolume", item_type="Number:Length", groups=["gCurrent", "gForecast_SnowVolume_1"], label="Current: Snow volume [%.1f %unit%]", category="Snow", tags=["OpenWeatherMap"])
            add_link("Current_SnowVolume", ChannelUID(owmThingUID + ":current#snow"))

        # create Forecast groups
        import calendar
        from org.joda.time import DateTime
        lastReading = DateTime(str(items["Current_Timestamp"])).getDayOfWeek() - 1
        for index in range(1, 6):
            dayOfWeek = "Today" if index == 1 else calendar.day_name[(lastReading + index - 1) % 7]
            if ir.getItems("gForecast_" + str(index)) == []:
                add_item("gForecast_" + str(index), item_type="Group", groups=["gOpenWeatherMap"], label=dayOfWeek, tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Timestamp_" + str(index)) == []:
                add_item("gForecast_Timestamp_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Timestamp [%1$tY-%1$tm-%1$td %1$tI:%1$tM%1$tp]", category="Time", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Condition_" + str(index)) == []:
                add_item("gForecast_Condition_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Condition [%s]", gi_base_type="String", category="Sun_Clouds", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_ConditionID_" + str(index)) == []:
                add_item("gForecast_ConditionID_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Condition ID [%s]", gi_base_type="String", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_IconID_" + str(index)) == []:
                add_item("gForecast_IconID_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Icon ID [%s]", gi_base_type="String", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Icon_" + str(index)) == []:
                add_item("gForecast_Icon_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Icon", gi_base_type="Image", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Temperature_High_" + str(index)) == []:
                add_item("gForecast_Temperature_High_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Temperature (high) [%.0f %unit%]", category="Temperature_Hot", gi_base_type="Number:Temperature", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Temperature_Low_" + str(index)) == []:
                add_item("gForecast_Temperature_Low_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Temperature (low) [%.0f %unit%]", category="Temperature_Cold", gi_base_type="Number:Temperature", group_function=ArithmeticGroupFunction.Min(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Pressure_" + str(index)) == []:
                add_item("gForecast_Pressure_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Pressure [%.1f %unit%]", category="Pressure", gi_base_type="Number:Pressure", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Humidity_" + str(index)) == []:
                add_item("gForecast_Humidity_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Humidity [%d %unit%]", category="Humidity", gi_base_type="Number:Dimensionless", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_WindSpeed_" + str(index)) == []:
                add_item("gForecast_WindSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Wind Speed [%.0f %unit%]", category="Wind", gi_base_type="Number:Speed", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_GustSpeed_" + str(index)) == []:
                add_item("gForecast_GustSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Gust Speed [%.0f %unit%]", category="Wind", gi_base_type="Number:Speed", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_WindDirection_" + str(index)) == []:
                #add_item("gForecast_WindDirection_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Wind direction [SCALE(windDirection.scale):%s]", category="Wind", gi_base_type="Number:Angle", group_function=ArithmeticGroupFunction.Avg(), tags=["OpenWeatherMap"])# this doesn't work properly yet
                add_item("gForecast_WindDirection_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Wind direction [SCALE(windDirection.scale):%s]", category="Wind", gi_base_type="Number:Angle", tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_Cloudiness_" + str(index)) == []:
                add_item("gForecast_Cloudiness_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Cloudiness [%d %unit%]", category="Sun_Clouds", gi_base_type="Number:Dimensionless", group_function=ArithmeticGroupFunction.Max(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_RainVolume_" + str(index)) == []:
                add_item("gForecast_RainVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Rain Volume [%.1f %unit%]", category="Rain", gi_base_type="Number:Length", group_function=ArithmeticGroupFunction.Sum(), tags=["OpenWeatherMap"])
            if ir.getItems("gForecast_SnowVolume_" + str(index)) == []:
                add_item("gForecast_SnowVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label=dayOfWeek + ": Snow Volume [%.1f %unit%]", category="Snow", gi_base_type="Number:Length", group_function=ArithmeticGroupFunction.Sum(), tags=["OpenWeatherMap"])

        # create Forecast Items
        for index in range(1, 41):
            if ir.getItems("Forecast_Timestamp_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Timestamp_{:02d}".format(3 * index), item_type="DateTime", label="Forecast ({:02d}): Timestamp [%1$tY-%1$tm-%1$td %1$tI:%1$tM%1$tp]".format(3 * index), category="Time", tags=["OpenWeatherMap"])
                add_link("Forecast_Timestamp_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#time-stamp".format(3 * index)))
            if ir.getItems("Forecast_Condition_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Condition_{:02d}".format(3 * index), item_type="String", label="Forecast ({:02d}): Condition [%s]".format(3 * index), category="Sun_Clouds", tags=["OpenWeatherMap"])
                add_link("Forecast_Condition_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#condition".format(3 * index)))
            if ir.getItems("Forecast_ConditionID_{:02d}".format(3 * index)) == []:
                add_item("Forecast_ConditionID_{:02d}".format(3 * index), item_type="String", label="Forecast ({:02d}): Condition ID [%s]".format(3 * index), tags=["OpenWeatherMap"])
                add_link("Forecast_ConditionID_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#condition-id".format(3 * index)))
            if ir.getItems("Forecast_IconID_{:02d}".format(3 * index)) == []:
                add_item("Forecast_IconID_{:02d}".format(3 * index), item_type="String", label="Forecast ({:02d}): Icon ID [%s]".format(3 * index), tags=["OpenWeatherMap"])
                add_link("Forecast_IconID_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#icon-id".format(3 * index)))
            if ir.getItems("Forecast_Icon_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Icon_{:02d}".format(3 * index), item_type="Image", label="Forecast ({:02d}): Icon".format(3 * index), tags=["OpenWeatherMap"])
                add_link("Forecast_Icon_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#icon".format(3 * index)))
            if ir.getItems("Forecast_Temperature_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Temperature_{:02d}".format(3 * index), item_type="Number:Temperature", label="Forecast ({:02d}): Temperature [%.0f %unit%]".format(3 * index), category="Temperature", tags=["OpenWeatherMap"])
                add_link("Forecast_Temperature_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#temperature".format(3 * index)))
            if ir.getItems("Forecast_Pressure_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Pressure_{:02d}".format(3 * index), item_type="Number:Pressure", label="Forecast ({:02d}): Pressure [%.1f %unit%]".format(3 * index), category="Pressure", tags=["OpenWeatherMap"])
                add_link("Forecast_Pressure_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#pressure".format(3 * index)))
            if ir.getItems("Forecast_Humidity_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Humidity_{:02d}".format(3 * index), item_type="Number:Dimensionless", label="Forecast ({:02d}): Humidity [%d %unit%]".format(3 * index), category="Humidity", tags=["OpenWeatherMap"])
                add_link("Forecast_Humidity_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#humidity".format(3 * index)))
            if ir.getItems("Forecast_WindSpeed_{:02d}".format(3 * index)) == []:
                add_item("Forecast_WindSpeed_{:02d}".format(3 * index), item_type="Number:Speed", label="Forecast ({:02d}): Wind speed [%.0f %unit%]".format(3 * index), category="Wind", tags=["OpenWeatherMap"])
                add_link("Forecast_WindSpeed_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#wind-speed".format(3 * index)))
            if ir.getItems("Forecast_GustSpeed_{:02d}".format(3 * index)) == []:
                add_item("Forecast_GustSpeed_{:02d}".format(3 * index), item_type="Number:Speed", label="Forecast ({:02d}): Gust speed [%.0f %unit%]".format(3 * index), category="Wind", tags=["OpenWeatherMap"])
                add_link("Forecast_GustSpeed_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#gust-speed".format(3 * index)))
            if ir.getItems("Forecast_WindDirection_{:02d}".format(3 * index)) == []:
                add_item("Forecast_WindDirection_{:02d}".format(3 * index), item_type="Number:Angle", label="Forecast ({:02d}): Wind direction [SCALE(windDirection.scale):%s]".format(3 * index), category="Wind", tags=["OpenWeatherMap"])
                add_link("Forecast_WindDirection_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#wind-direction".format(3 * index)))
            if ir.getItems("Forecast_Cloudiness_{:02d}".format(3 * index)) == []:
                add_item("Forecast_Cloudiness_{:02d}".format(3 * index), item_type="Number:Dimensionless", label="Forecast ({:02d}): Cloudiness [%d %unit%]".format(3 * index), category="Sun_Clouds", tags=["OpenWeatherMap"])
                add_link("Forecast_Cloudiness_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#cloudiness".format(3 * index)))
            if ir.getItems("Forecast_RainVolume_{:02d}".format(3 * index)) == []:
                add_item("Forecast_RainVolume_{:02d}".format(3 * index), item_type="Number:Length", label="Forecast ({:02d}): Rain volume [%.1f %unit%]".format(3 * index), category="Rain", tags=["OpenWeatherMap"])
                add_link("Forecast_RainVolume_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#rain".format(3 * index)))
            if ir.getItems("Forecast_SnowVolume_{:02d}".format(3 * index)) == []:
                add_item("Forecast_SnowVolume_{:02d}".format(3 * index), item_type="Number:Length", label="Forecast ({:02d}): Snow volume [%.1f %unit%]".format(3 * index), category="Snow", tags=["OpenWeatherMap"])
                add_link("Forecast_SnowVolume_{:02d}".format(3 * index), ChannelUID(owmThingUID + ":forecastHours{:02d}#snow".format(3 * index)))

        from core.rules import rule
        from core.triggers import when

        @rule("Add OpenWeatherMap Items to daily forecast groups")
        @when("Item Current_Timestamp changed")
        def addOWMItemsToGroups(event):
            # remove hourly forecast Items from groups
            for groupIndex in range(1, 6):
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Condition_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Condition_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_IconID_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_IconID_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Icon_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Icon_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Temperature_High_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Temperature_High_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Temperature_Low_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Temperature_Low_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Pressure_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Pressure_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Humidity_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Humidity_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).removeMember(member)
                for member in filter(lambda item: "Current" not in item.name, ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).getMembers()):
                    ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).removeMember(member)

            # update group labels to reflect week day
            from org.joda.time import DateTime
            import calendar
            lastReading = DateTime(str(items["Current_Timestamp"])).getDayOfWeek() - 1
            for index in range(1, 6):
                dayOfWeek = "Today" if index == 1 else calendar.day_name[(lastReading + index - 1) % 7]
                ir.getItem("gForecast_" + str(index)).setLabel(dayOfWeek)
                ir.getItem("gForecast_Timestamp_" + str(index)).setLabel(dayOfWeek + ": Timestamp")
                ir.getItem("gForecast_Condition_" + str(index)).setLabel(dayOfWeek + ": Condition [%s]")
                ir.getItem("gForecast_ConditionID_" + str(index)).setLabel(dayOfWeek + ": Condition ID [%s]")
                ir.getItem("gForecast_IconID_" + str(index)).setLabel(dayOfWeek + ": Icon ID [%s]")
                ir.getItem("gForecast_Icon_" + str(index)).setLabel(dayOfWeek + ": Icon")
                ir.getItem("gForecast_Temperature_High_" + str(index)).setLabel(dayOfWeek + ": Temperature (high) [%.0f %unit%]")
                ir.getItem("gForecast_Temperature_Low_" + str(index)).setLabel(dayOfWeek + ": Temperature (low) [%.0f %unit%]")
                ir.getItem("gForecast_Pressure_" + str(index)).setLabel(dayOfWeek + ": Pressure [%.1f %unit%]")
                ir.getItem("gForecast_Humidity_" + str(index)).setLabel(dayOfWeek + ": Humidity [%d %unit%]")
                ir.getItem("gForecast_WindSpeed_" + str(index)).setLabel(dayOfWeek + ": Wind Speed [%.0f %unit%]")
                ir.getItem("gForecast_GustSpeed_" + str(index)).setLabel(dayOfWeek + ": Gust Speed [%.0f %unit%]")
                ir.getItem("gForecast_WindDirection_" + str(index)).setLabel(dayOfWeek + ": Wind direction [SCALE(windDirection.scale):%s]")
                ir.getItem("gForecast_Cloudiness_" + str(index)).setLabel(dayOfWeek + ": Cloudiness [%d %unit%]")
                ir.getItem("gForecast_RainVolume_" + str(index)).setLabel(dayOfWeek + ": Rain Volume [%.1f %unit%]")
                ir.getItem("gForecast_SnowVolume_" + str(index)).setLabel(dayOfWeek + ": Snow Volume [%.1f %unit%]")

            # add Forecast Items to groups, and update the labels to reflect time
            groupIndex = 1
            for index in range(1, 41):
                if DateTime(str(items["Forecast_Timestamp_{:02}".format(3 * index)])).getDayOfWeek() - 1 != (DateTime.now().getDayOfWeek() + groupIndex - 2) % 7:
                    if groupIndex == 5:
                        break# we're at the end of the forecasts that fit into 5 days
                    else:
                        groupIndex += 1
                labelTime = items["Forecast_Timestamp_{:02}".format(3 * index)].format("%1$tl:%1$tM%1$tp")

                ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Timestamp_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Timestamp_{:02d}".format(3 * index)).setLabel("Forecast ({}): Timestamp [%1$tY-%1$tm-%1$td %1$tI:%1$tM%1$tp]".format(labelTime))

                ir.getItem("gForecast_Condition_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Condition_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Condition_{:02d}".format(3 * index)).setLabel("Forecast ({}): Condition [%s]".format(labelTime))

                ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).addMember(ir.getItem("Forecast_ConditionID_{:02d}".format(3 * index)))
                ir.getItem("Forecast_ConditionID_{:02d}".format(3 * index)).setLabel("Forecast ({}): Condition ID [%s]".format(labelTime))

                ir.getItem("gForecast_IconID_{}".format(groupIndex)).addMember(ir.getItem("Forecast_IconID_{:02d}".format(3 * index)))
                ir.getItem("Forecast_IconID_{:02d}".format(3 * index)).setLabel("Forecast ({}): Icon ID [%s]".format(labelTime))

                ir.getItem("gForecast_Icon_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Icon_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Icon_{:02d}".format(3 * index)).setLabel("Forecast ({}): Icon".format(labelTime))

                ir.getItem("gForecast_Temperature_High_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Temperature_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Temperature_{:02d}".format(3 * index)).setLabel("Forecast ({}): Temperature [%.0f %unit%]".format(labelTime))

                ir.getItem("gForecast_Temperature_Low_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Temperature_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Temperature_{:02d}".format(3 * index)).setLabel("Forecast ({}): Temperature [%.0f %unit%]".format(labelTime))

                ir.getItem("gForecast_Pressure_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Pressure_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Pressure_{:02d}".format(3 * index)).setLabel("Forecast ({}): Pressure [%.1f %unit%]".format(labelTime))

                ir.getItem("gForecast_Humidity_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Humidity_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Humidity_{:02d}".format(3 * index)).setLabel("Forecast ({}): Humidity [%d %unit%]".format(labelTime))

                ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).addMember(ir.getItem("Forecast_WindSpeed_{:02d}".format(3 * index)))
                ir.getItem("Forecast_WindSpeed_{:02d}".format(3 * index)).setLabel("Forecast ({}): Wind speed [%.0f %unit%]".format(labelTime))

                ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).addMember(ir.getItem("Forecast_GustSpeed_{:02d}".format(3 * index)))
                ir.getItem("Forecast_GustSpeed_{:02d}".format(3 * index)).setLabel("Forecast ({}): Gust speed [%.0f %unit%]".format(labelTime))

                ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).addMember(ir.getItem("Forecast_WindDirection_{:02d}".format(3 * index)))
                ir.getItem("Forecast_WindDirection_{:02d}".format(3 * index)).setLabel("Forecast ({}): Wind direction [SCALE(windDirection.scale):%s]".format(labelTime))

                ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Cloudiness_{:02d}".format(3 * index)))
                ir.getItem("Forecast_Cloudiness_{:02d}".format(3 * index)).setLabel("Forecast ({}): Cloudiness [%d %unit%]".format(labelTime))
                
                ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).addMember(ir.getItem("Forecast_RainVolume_{:02d}".format(3 * index)))
                ir.getItem("Forecast_RainVolume_{:02d}".format(3 * index)).setLabel("Forecast ({}): Rain volume [%.1f %unit%]".format(labelTime))

                ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).addMember(ir.getItem("Forecast_SnowVolume_{:02d}".format(3 * index)))
                ir.getItem("Forecast_SnowVolume_{:02d}".format(3 * index)).setLabel("Forecast ({}): Snow volume [%.1f %unit%]".format(labelTime))

            # set Condition, Icon and WindDirection group values
            for index in range(1, 6):
                for group in [600, 200, 500, 300, 700, 800]:# the Conditions are organized into groups (https://openweathermap.org/weather-conditions), which I have prioritized
                    forecastItems = filter(lambda item: int(item.state.toString()) in range(group, group + 100), ir.getItem("gForecast_ConditionID_" + str(index)).getMembers())
                    if len(forecastItems) > 0:
                        sortedItems = sorted(forecastItems, key = lambda item: int(item.state.toString()))
                        selectedItem = sortedItems.pop()# this will provide the highest value in the sorted list of Items, which is usually the most severe condition
                        events.postUpdate("gForecast_ConditionID_" + str(index), selectedItem.state.toString())
                        events.postUpdate("gForecast_Condition_" + str(index), items[selectedItem.name.replace("ID", "")].toString())
                        events.postUpdate("gForecast_IconID_" + str(index), items[selectedItem.name.replace("Condition", "Icon")].toString())
                        events.postUpdate(ir.getItem("gForecast_Icon_" + str(index)), items[selectedItem.name.replace("ConditionID", "Icon")])
                        break
                # this can be removed when ArithmeticGroupFunction.Avg() is fixed for Number:Angle
                windDirectionItemStates = map(lambda item: item.state.intValue(), filter(lambda member: member.state != NULL and member.state != UNDEF, ir.getItem("gForecast_WindDirection_" + str(index)).getMembers()))
                if len(windDirectionItemStates) > 0:
                    windDirectionAvg = reduce(lambda x, y: (((x + y) / 2) if y - x < 180 else (x + y + 360) / 2) % 360, windDirectionItemStates)
                    events.postUpdate("gForecast_WindDirection_" + str(index), str(windDirectionAvg))
            
            addOWMItemsToGroups.log.debug("Updated groups and Items")

        addOWMItemsToGroups(None)

addOWMItems()
