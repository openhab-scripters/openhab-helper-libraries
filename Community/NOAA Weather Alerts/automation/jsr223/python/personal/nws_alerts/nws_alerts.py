"""
Purpose
-------

This script creates a rule that sends a notification when an NWS RSS feed
updates with a weather alert.


Requires
--------

* `openHAB Cloud Connector <https://www.openhab.org/addons/bindings/amazonechocontrol/>`_
* myopenhab.org setup with at least one mobile device
* Find the URL for the area that you want the alert for... https://alerts.weather.gov/, then scroll down and select your state, then county, then copy the URL from the address in your browser
* Create a feed Thing using the URL from above (for example, this is for our area... https://alerts.weather.gov/cap/wwaatmget.php?x=OHC103&y=1)
* Items:

  .. code-block::

      Group    gNWS_Public_Alert    "NWS Public Alert RSS Feed"    <text>    (gFeed)
      String    Feed_NWS_Public_Description_Latest    "NWS: Latest description [%s]"    <text>    (gNWS_Public_Alert)    {channel="feed:feed:nws-public-alert:latest-description"}
      DateTime    Feed_NWS_Public_Date_Latest    "NWS: Latest date [%1$tA, %1$tB %1$te, %1$tY at %1$tl:%1$tM%1$tp]"    <calendar>    (gNWS_Public_Alert)    {channel="feed:feed:nws-public-alert:latest-date"}


  You probably won't need the Feed_NWS_Public_Date_Latest Item, but I use it in an announcement that plays periodically throughout the day when the ``mode changes <https://openhab-scripters.github.io/openhab-helper-libraries/Python/Community/Mode%20(Time%20of%20Day).html>_

  .. code-block::

      if items["Feed_NWS_Public_Date_Latest"].zonedDateTime.isAfter(DateTimeType().zonedDateTime.minusDays(1)):
          temp_reminder = "{}\nReminder: {}".format(temp_reminder, items["Feed_NWS_Public_Title_Latest"])
"""
from core.rules import rule
from core.triggers import when
from core.actions import NotificationAction

@rule("Alert: NWS public alert")
@when("Item Feed_NWS_Public_Description_Latest changed")
def nws_update(event):
    NotificationAction.sendBroadcastNotification(u"Weather Alert: {}".format(items["Feed_NWS_Public_Description_Latest"].toString()))
