'''
PURPOSE:
This rule will create and link the ~600 Items and groups needed to get daily
forecasts from the OWM binding using a free API key. It will also install the
Scale transformation service, if it is not already installed. There is also a
function that was used for testing purposes, which can be used to remove all
the Items and groups. As the day progresses, there will be fewer hourly
forecasts included in the gForecast_1 group.

The rule will arrange Items into the following group structure for days(X) 1-5.
gForecast_1 contains Items for the rest of the day, and the other groups
contain Items for subsequent days.

gOpenWeatherMap
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
        'Number of Hours' set to 120 and 'Number of Days' set to 0
    All OWM Items should be removed before using rule

There are several groups and Items commented out, but these can be removed
based on personal preference.

KNOWN ISSUES:
ArithmethicGroupFunction.Avg does not properly average angles. An ESH issue has
been opened for this.
'''

def removeOWMItems():
    if ir.getItems("gOpenWeatherMap"):
        log = logging.getLogger(LOG_PREFIX + ".removeOWMItems")
        from core.items import remove

        for item in ir.getItem("gOpenWeatherMap").getAllMembers():
            log.debug("Test: item.name=[{}]".format(item.name))
            remove(item)

        for group in ir.getItem("gOpenWeatherMap").getMembers():
            for subgroup in group.getMembers():
                log.debug("Test: subgroup.name=[{}]".format(subgroup.name))
                remove(subgroup)
            log.debug("Test: group.name=[{}]".format(group.name))
            remove(item)

        remove(ir.getItem("gOpenWeatherMap"))
    
#removeOWMItems()

from core.rules import rule
from core.triggers import when

@rule("Add OpenWeatherMap Items to daily forecast groups")
@when("Time cron 20 0 0/3 * * ?")
def addOWMItemsToGroups(event):
    if not ir.getItems("gOpenWeatherMap"):
        # install Scale transformation service, if not already
        import json

        from org.eclipse.smarthome.model.script.actions.Exec import executeCommandLine

        scaleCheckResult = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 10 -m 10 -X GET -H \"Accept: application/json\" \"http://localhost:8080/rest/extensions/transformation-scale\"",15000)
        if not scaleCheckResult:
            addOWMItemsToGroups.log.debug("Scale transformation is not installed")
            installScaleResult = executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -o /dev/null -s -w \"%{http_code}\" --connect-timeout 10 -m 10 -X POST -H \"Content-Type: application/json\" -H \"Accept: application/json\" \"http://localhost:8080/rest/extensions/transformation-scale/install\"",15000)
            if installScaleResult != "200":
                addOWMItemsToGroups.log.debug("Scale transformation installation failed")
                return
            else:
                addOWMItemsToGroups.log.debug("Scale transformation has been installed")

        # create OWM Items and groups, if they do not exist
        from org.eclipse.smarthome.core.thing.link import ItemChannelLink
        from org.eclipse.smarthome.core.thing import ChannelUID
        from org.eclipse.smarthome.core.thing import ThingUID
        from org.eclipse.smarthome.core.thing import ThingTypeUID
        from org.eclipse.smarthome.core.library.types import ArithmeticGroupFunction

        from core.items import add
        from core import osgi
        from org.joda.time import DateTime

        ItemChannelLinkRegistry = osgi.get_service("org.eclipse.smarthome.core.thing.link.ItemChannelLinkRegistry")

        owmThingID = None
        for thing in things.getAll():
            if thing.getThingTypeUID() == ThingTypeUID("openweathermap:weather-and-forecast"):
                owmThingID = thing.getUID().getId()

        add("gOpenWeatherMap", item_type="Group", groups=["gWeather"], label="OpenWeatherMap")

        if not ir.getItems("Current_Timestamp"):
            add("Current_Timestamp", item_type="DateTime", groups=["gOpenWeatherMap"], label="Current: Timestamp [%1$tY-%1$tm-%1$tdT%1$tH:%1$tM:%1$tS]")
            ItemChannelLink("Current_Timestamp", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#time-stamp"))
        if not ir.getItems("Current_Condition"):
            add("Current_Condition", item_type="String", groups=["gOpenWeatherMap"], label="Current: Condition [%s]")
            ItemChannelLink("Current_Condition", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#condition"))
        #if not ir.getItems("Current_ConditionID"):
        #    add("Current_ConditionID", item_type="String", groups=["gOpenWeatherMap"], label="Current: Condition ID [%s]")
        #    ItemChannelLink("Current_ConditionID", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#condition-id"))
        #if not ir.getItems("Current_Icon"):
        #    add("Current_Icon", item_type="Image", groups=["gOpenWeatherMap"], label="Current: Icon")
        #    ItemChannelLink("Current_Icon", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#icon"))
        if not ir.getItems("Current_Temperature"):
            add("Current_Temperature", item_type="Number:Temperature", groups=["gOpenWeatherMap"], label="Current: Temperature [%.0f %unit%]")
            ItemChannelLink("Current_Temperature", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#temperature"))
        if not ir.getItems("Current_Pressure"):
            add("Current_Pressure", item_type="Number:Pressure", groups=["gOpenWeatherMap"], label="Current: Pressure [%.1f %unit%]")
            ItemChannelLink("Current_Pressure", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#pressure"))
        if not ir.getItems("Current_Humidity"):
            add("Current_Humidity", item_type="Number:Dimensionless", groups=["gOpenWeatherMap"], label="Current: Humidity [%d %unit%]")
            ItemChannelLink("Current_Humidity", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#humidity"))
        if not ir.getItems("Current_WindSpeed"):
            add("Current_WindSpeed", item_type="Number:Speed", groups=["gOpenWeatherMap"], label="Current: Wind speed [%.0f %unit%]")
            ItemChannelLink("Current_WindSpeed", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#wind-speed"))
        #if not ir.getItems("Current_GustSpeed"):
        #    add("Current_GustSpeed", item_type="Number:Speed", groups=["gOpenWeatherMap"], label="Current: Gust speed [%.0f %unit%]")
        #    ItemChannelLink("Current_GustSpeed", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#gust-speed"))
        if not ir.getItems("Current_WindDirection"):
            add("Current_WindDirection", item_type="Number:Angle", groups=["gOpenWeatherMap"], label="Current: Wind direction [SCALE(windDirection.scale):%s]")
            ItemChannelLink("Current_WindDirection", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#wind-direction"))
        if not ir.getItems("Current_Cloudiness"):
            add("Current_Cloudiness", item_type="Number:Dimensionless", groups=["gOpenWeatherMap"], label="Current: Cloudiness [%d %unit%]")
            ItemChannelLink("Current_Cloudiness", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#cloudiness"))
        if not ir.getItems("Current_RainVolume"):
            add("Current_RainVolume", item_type="Number:Length", groups=["gOpenWeatherMap"], label="Current: Rain volume [%.1f %unit%]")
            ItemChannelLink("Current_RainVolume", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#rain"))
        if not ir.getItems("Current_SnowVolume"):
            add("Current_SnowVolume", item_type="Number:Length", groups=["gOpenWeatherMap"], label="Current: Snow volume [%.1f %unit%]")
            ItemChannelLink("Current_SnowVolume", ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":current#snow"))

        for index in range(1, 6):
            if not ir.getItems("gForecast_" + str(index)):
                add("gForecast_" + str(index), item_type="Group", groups=["gOpenWeatherMap"], label="Forecast " + str(index))
            #if not ir.getItems("gForecast_Timestamp_" + str(index)):
            #    add("gForecast_Timestamp_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Timestamp [%.0f %unit%]")
            #if not ir.getItems("gForecast_Condition_" + str(index)):
            #    add("gForecast_Condition_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Condition [%.0f %unit%]")
            #if not ir.getItems("gForecast_ConditionID_" + str(index)):
            #    add("gForecast_ConditionID_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Condition ID [%.0f %unit%]")
            #if not ir.getItems("gForecast_Icon_" + str(index)):
            #    add("gForecast_Icon_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Icon [%.0f %unit%]")
            if not ir.getItems("gForecast_Temperature_" + str(index)):
                add("gForecast_Temperature_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Temperature [%.0f %unit%]", gi_base_type="Number:Temperature", group_function=ArithmeticGroupFunction.Max())
            if not ir.getItems("gForecast_Pressure_" + str(index)):
                add("gForecast_Pressure_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Pressure [%.1f %unit%]", gi_base_type="Number:Pressure", group_function=ArithmeticGroupFunction.Max())
            if not ir.getItems("gForecast_Humidity_" + str(index)):
                add("gForecast_Humidity_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Humidity [%d %unit%]", gi_base_type="Number:Dimensionless", group_function=ArithmeticGroupFunction.Max())
            if not ir.getItems("gForecast_WindSpeed_" + str(index)):
                add("gForecast_WindSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Wind Speed [%.0f %unit%]", gi_base_type="Number:Speed", group_function=ArithmeticGroupFunction.Max())
            #if not ir.getItems("gForecast_GustSpeed_" + str(index)):
            #    add("gForecast_GustSpeed_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Gust Speed [%.0f %unit%]", gi_base_type="Number:Speed", group_function=ArithmeticGroupFunction.Max())
            if not ir.getItems("gForecast_WindDirection_" + str(index)):
                add("gForecast_WindDirection_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Wind direction [%.0f %unit%]", gi_base_type="Number:Angle", group_function=ArithmeticGroupFunction.Avg())
            if not ir.getItems("gForecast_Cloudiness_" + str(index)):
                add("gForecast_Cloudiness_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Cloudiness [%d %unit%]", gi_base_type="Number:Dimensionless", group_function=ArithmeticGroupFunction.Max())
            if not ir.getItems("gForecast_RainVolume_" + str(index)):
                add("gForecast_RainVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Rain Volume [%.1f %unit%]", gi_base_type="Number:Length", group_function=ArithmeticGroupFunction.Sum())
            if not ir.getItems("gForecast_SnowVolume_" + str(index)):
                add("gForecast_SnowVolume_" + str(index), item_type="Group", groups=["gForecast_" + str(index)], label="Forecast " + str(index) + ": Snow Volume [%.1f %unit%]", gi_base_type="Number:Length", group_function=ArithmeticGroupFunction.Sum())

        for index in range(1, 41):
            #if not ir.getItems("Forecast_Timestamp_{:03d}".format(3 * index)):
            #    add("Forecast_Timestamp_{:03d}".format(3 * index), item_type="DateTime", label="Forecast ({:03d}): Timestamp [%1$tY-%1$tm-%1$tdT%1$tH:%1$tM:%1$tS]".format(3 * index))
            #    ItemChannelLink("Forecast_Timestamp_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#time-stamp".format(3 * index)))
            #if not ir.getItems("Forecast_Condition_{:03d}".format(3 * index)):
            #    add("Forecast_Condition_{:03d}".format(3 * index), item_type="String", label="Forecast ({:03d}): Condition [%s]".format(3 * index))
            #    ItemChannelLink("Forecast_Condition_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#condition".format(3 * index)))
            #if not ir.getItems("Forecast_ConditionID_{:03d}".format(3 * index)):
            #    add("Forecast_ConditionID_{:03d}".format(3 * index), item_type="String", label="Forecast ({:03d}): Condition ID [%s]".format(3 * index))
            #    ItemChannelLink("Forecast_ConditionID_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#condition-id".format(3 * index)))
            #if not ir.getItems("Forecast_Icon_{:03d}".format(3 * index)):
            #    add("Forecast_Icon_{:03d}".format(3 * index), item_type="Image", label="Forecast ({:03d}): Icon".format(3 * index))
            #    ItemChannelLink("Forecast_Icon_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#icon".format(3 * index)))
            if not ir.getItems("Forecast_Temperature_{:03d}".format(3 * index)):
                add("Forecast_Temperature_{:03d}".format(3 * index), item_type="Number:Temperature", label="Forecast ({:03d}): Temperature [%.0f %unit%]".format(3 * index))
                ItemChannelLink("Forecast_Temperature_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#temperature".format(3 * index)))
            if not ir.getItems("Forecast_Pressure_{:03d}".format(3 * index)):
                add("Forecast_Pressure_{:03d}".format(3 * index), item_type="Number:Pressure", label="Forecast ({:03d}): Pressure [%.1f %unit%]".format(3 * index))
                ItemChannelLink("Forecast_Pressure_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#pressure".format(3 * index)))
            if not ir.getItems("Forecast_Humidity_{:03d}".format(3 * index)):
                add("Forecast_Humidity_{:03d}".format(3 * index), item_type="Number:Dimensionless", label="Forecast ({:03d}): Humidity [%d %unit%]".format(3 * index))
                ItemChannelLink("Forecast_Humidity_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#humidity".format(3 * index)))
            if not ir.getItems("Forecast_WindSpeed_{:03d}".format(3 * index)):
                add("Forecast_WindSpeed_{:03d}".format(3 * index), item_type="Number:Speed", label="Forecast ({:03d}): Wind speed [%.0f %unit%]".format(3 * index))
                ItemChannelLink("Forecast_WindSpeed_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#wind-speed".format(3 * index)))
            #if not ir.getItems("Forecast_GustSpeed_{:03d}".format(3 * index)):
            #    add("Forecast_GustSpeed_{:03d}".format(3 * index), item_type="Number:Speed", label="Forecast ({:03d}): Gust speed [%.0f %unit%]".format(3 * index))
            #    ItemChannelLink("Forecast_GustSpeed_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#gust-speed".format(3 * index)))
            if not ir.getItems("Forecast_WindDirection_{:03d}".format(3 * index)):
                add("Forecast_WindDirection_{:03d}".format(3 * index), item_type="Number:Angle", label="Forecast ({:03d}): Wind direction [SCALE(windDirection.scale):%s]".format(3 * index))
                ItemChannelLink("Forecast_WindDirection_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#wind-direction".format(3 * index)))
            if not ir.getItems("Forecast_Cloudiness_{:03d}".format(3 * index)):
                add("Forecast_Cloudiness_{:03d}".format(3 * index), item_type="Number:Dimensionless", label="Forecast ({:03d}): Cloudiness [%d %unit%]".format(3 * index))
                ItemChannelLink("Forecast_Cloudiness_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#cloudiness".format(3 * index)))
            if not ir.getItems("Forecast_RainVolume_{:03d}".format(3 * index)):
                add("Forecast_RainVolume_{:03d}".format(3 * index), item_type="Number:Length", label="Forecast ({:03d}): Rain volume [%.1f %unit%]".format(3 * index))
                ItemChannelLink("Forecast_RainVolume_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#rain".format(3 * index)))
            if not ir.getItems("Forecast_SnowVolume_{:03d}".format(3 * index)):
                add("Forecast_SnowVolume_{:03d}".format(3 * index), item_type="Number:Length", label="Forecast ({:03d}): Snow volume [%.1f %unit%]".format(3 * index))
                ItemChannelLink("Forecast_SnowVolume_{:03d}".format(3 * index), ChannelUID("openweathermap:weather-and-forecast:" + owmThingID + ":forecastHours{:02d}#snow".format(3 * index)))

    currentHour = DateTime.now().getHourOfDay()
    forecastsLeftInDay = 8 - int(math.floor(currentHour / 3))# max 8, min 1
    addOWMItemsToGroups.log.debug("currentHour=[{}], forecastsLeftInDay=[{}]".format(currentHour, forecastsLeftInDay))

    # remove hourly forecast Items from groups
    for groupIndex in range(1, 6):
        #for member in ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).getMembers():
        #    ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).removeMember(member)
        #for member in ir.getItem("gForecast_Condition_{}".format(groupIndex)).getMembers():
        #    ir.getItem("gForecast_Condition_{}".format(groupIndex)).removeMember(member)
        #for member in ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).getMembers():
        #    ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).removeMember(member)
        #for member in ir.getItem("gForecast_Icon_{}".format(groupIndex)).getMembers():
        #    ir.getItem("gForecast_Icon_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_Temperature_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_Temperature_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_Pressure_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_Pressure_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_Humidity_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_Humidity_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).removeMember(member)
        #for member in ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).getMembers():
        #    ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).removeMember(member)
        for member in ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).getMembers():
            ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).removeMember(member)

    for groupIndex in range(1, 6):
        for index in range(1 + (0 if groupIndex == 1 else forecastsLeftInDay + 8 * (groupIndex - 2)), forecastsLeftInDay + 1 + 8 * (groupIndex - 1)):
            #ir.getItem("gForecast_Timestamp_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Timestamp_{:03d}".format(3 * index)))
            #ir.getItem("gForecast_Condition_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Condition_{:03d}".format(3 * index)))
            #ir.getItem("gForecast_ConditionID_{}".format(groupIndex)).addMember(ir.getItem("Forecast_ConditionID_{:03d}".format(3 * index)))
            #ir.getItem("gForecast_Icon_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Icon_{:03d}".format(3 * index)))
            ir.getItem("gForecast_Temperature_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Temperature_{:03d}".format(3 * index)))
            ir.getItem("gForecast_Pressure_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Pressure_{:03d}".format(3 * index)))
            ir.getItem("gForecast_Humidity_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Humidity_{:03d}".format(3 * index)))
            ir.getItem("gForecast_WindSpeed_{}".format(groupIndex)).addMember(ir.getItem("Forecast_WindSpeed_{:03d}".format(3 * index)))
            #ir.getItem("gForecast_GustSpeed_{}".format(groupIndex)).addMember(ir.getItem("Forecast_GustSpeed_{:03d}".format(3 * index)))
            ir.getItem("gForecast_WindDirection_{}".format(groupIndex)).addMember(ir.getItem("Forecast_WindDirection_{:03d}".format(3 * index)))
            ir.getItem("gForecast_Cloudiness_{}".format(groupIndex)).addMember(ir.getItem("Forecast_Cloudiness_{:03d}".format(3 * index)))
            ir.getItem("gForecast_RainVolume_{}".format(groupIndex)).addMember(ir.getItem("Forecast_RainVolume_{:03d}".format(3 * index)))
            ir.getItem("gForecast_SnowVolume_{}".format(groupIndex)).addMember(ir.getItem("Forecast_SnowVolume_{:03d}".format(3 * index)))

            #addOWMItemsToGroups.log.debug("[{}], [{:03d}]".format(groupIndex, 3 * index))

addOWMItemsToGroups(None)
