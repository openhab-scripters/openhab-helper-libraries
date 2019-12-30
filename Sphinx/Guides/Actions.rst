*******
Actions
*******

Use `Core & Cloud Actions <https://www.openhab.org/docs/configuration/actions.html#core-actions>`_
--------------------------------------------------------------------------------------------------------

For ScriptExecution, see :ref:`Guides/But How Do I:Use a timer`.
For LogAction, see :ref:`Guides/Logging:LogAction`.

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.actions import Exec
            Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://host.example.com",5000)

            from core.actions import HTTP
            HTTP.sendHttpPutRequest("someURL.example.com, "application/json", '{"this": "that"}')

            from core.actions import Ping
            if Ping.checkVitality("10.5.5.5", 0, 5000):
                log.info("Server is online")
            else:
                log.info("Server is offline")

            from core.actions import Audio
            Audio.playSound("doorbell.mp3")# using the default audiosink
            Audio.playSound("my:audio:sink", "doorbell.mp3")# specifying an audiosink
            Audio.playStream("http://myAudioServer.example.com/myAudioFile.mp3")# using the default audiosink
            Audio.playStream("my:audio:sink", "http://myAudioServer.example.com/myAudioFile.mp3")# specifying an audiosink

            from core.actions import NotificationAction
            NotificationAction.sendNotification("someone@example.com","This is the message")
            NotificationAction.sendBroadcastNotification("This is the message")
            NotificationAction.sendLogNotification("This is the message")

            from core.actions import Transformation
            Transformation.transform("JSONPATH", "$.test", test)

            from core.actions import Voice
            Voice.say("This will be said")

            from core.actions import Things
            Things.getThingStatusInfo("zwave:device:c5155aa4:node5")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            var OPENHAB_CONF = Java.type('java.lang.System').getenv('OPENHAB_CONF');
            load(OPENHAB_CONF + '/automation/lib/javascript/core/actions.js');

            Exec.executeCommandLine("/bin/sh@@-c@@/usr/bin/curl -s --connect-timeout 3 --max-time 3 http://host.example.com",5000);

            HTTP.sendHttpPutRequest("someURL.example.com, "application/json", '{"this": "that"}');

            if (Ping.checkVitality("10.5.5.5", 0, 5000)) {
                LogAction.logInfo("Rules", "Server is online");
            } else {
                LogAction.logInfo("Rules", "Server is offline");
            }

            Audio.playSound("doorbell.mp3");// using the default audiosink
            Audio.playSound("my:audio:sink", "doorbell.mp3");// specifying an audiosink
            Audio.playStream("http://myAudioServer.example.com/myAudioFile.mp3");// using the default audiosink
            Audio.playStream("my:audio:sink", "http://myAudioServer.example.com/myAudioFile.mp3");// specifying an audiosink

            NotificationAction.sendNotification("someone@example.com", "This is the message");
            NotificationAction.sendBroadcastNotification("This is the message");
            NotificationAction.sendLogNotification("This is the message");

            LogAction.logInfo("Rules", Transformation.transform("JSONPATH", "$.test", test));

            Voice.say("This will be said");

            LogAction.logInfo("Rules", Things.getThingStatusInfo("zwave:device:c5155aa4:node5").toString());

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            TODO


`Persistence extensions <https://www.openhab.org/docs/configuration/persistence.html#persistence-extensions-in-scripts-and-rules>`_
-----------------------------------------------------------------------------------------------------------------------------------

Others not listed are similar

.. tabs::

    .. group-tab:: Python

        .. code-block::

            from core.actions import PersistenceExtensions
            PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state

            from org.joda.time import DateTime
            PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1))
            PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).state

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            var OPENHAB_CONF = Java.type('java.lang.System').getenv('OPENHAB_CONF');
            load(OPENHAB_CONF + '/automation/lib/javascript/core/actions.js');

            LogAction.logInfo("Rules", PersistenceExtensions.previousState(ir.getItem("Weather_SolarRadiation"), True).state.toString());

            var DateTime = Java.type('org.joda.time.DateTime');

            LogAction.logInfo("Rules", PersistenceExtensions.changedSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)));
            LogAction.logInfo("Rules", PersistenceExtensions.maximumSince(ir.getItem("Weather_SolarRadiation"), DateTime.now().minusHours(1)).state.toString());

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend

            TODO


Use an Addon/Bundle Action
--------------------------

 The binding or Action must be installed.
 There are two different types of Actions, old 1.x style Actions and new 2.x style Actions that come inside of 2.x bindings.
 For the 1.x version Actions you must explicetly import the Action to use it (see Astro below).
 For 2.x bindings, the Actions are accessible through the actions variable.

.. tabs::

    .. group-tab:: Python

        `Telegram <https://www.openhab.org/addons/bindings/telegram/>`_

        .. code-block::

            # New Telegram Binding Action
            actions.get("telegram", "telegram:telegramBot:xxxxx").sendTelegram("MyBot", "Test")

            # Deprecated due to new Telegram Binding
            from core.actions import Telegram
            Telegram.sendTelegram("MyBot", "Test")

        `Pushover <https://www.openhab.org/addons/actions/pushover/#pushover-actions>`_

        .. code-block::

            from core.actions import Pushover
            Pushover.sendPushoverMessage(Pushover.pushoverBuilder("Test"))

        `Pushbullet <https://www.openhab.org/addons/bindings/pushbullet/>`_

        .. code-block::

            # New Pushbullet Binding Action
            actions.get("pushbullet", "pushbullet:bot:r2d2").sendPushbulletNote("someone@example.com", "R2D2 talks here...", "This is the pushed note.")

            # Deprecated due to new Pushbullet Binding
            from core.actions import PushbulletAPIConnector
            PushbulletAPIConnector.sendPushbulletNote("someone@example.com", "openHAB", "Test")

        `Mail <https://www.openhab.org/addons/bindings/mail/>`_

        .. code-block::

            # New Mail Binding Action
            actions.get("mail", "mail:smtp:mail_thing").sendMail("someone@example.com", "This is the subject", "This is the message")

            # Deprecated due to new Mail Binding
            from core.actions import Mail
            Mail.sendMail("someone@example.com", "This is the subject", "This is the message")

        `Astro <https://www.openhab.org/addons/actions/astro/#astro-actions>`_

        .. code-block::

            from core.actions import Astro
            from core.log import logging, LOG_PREFIX
            from java.util import Date

            log = logging.getLogger("{}.astro_test".format(LOG_PREFIX))

            # Use the Astro action to get the sunset start time.
            log.info("Sunset: {}".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))

        `MQTT2 <https://www.openhab.org/addons/bindings/mqtt/>`_

        .. code-block::

            # no import needed
            actions.get("mqtt", "mqtt:systemBroker:embedded-mqtt-broker").publishMQTT("test/system/started", "true")

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

        `Telegram <https://www.openhab.org/addons/bindings/telegram/>`_

        .. code-block::

            // New Telegram Binding Action
            actions.get("telegram", "telegram:telegramBot:xxxxx").sendTelegram("MyBot", "Test")

            // Deprecated due to new Telegram Binding Action
            var OPENHAB_CONF = Java.type('java.lang.System').getenv('OPENHAB_CONF');
            load(OPENHAB_CONF + '/automation/lib/javascript/core/actions.js');

            Telegram.sendTelegram("MyBot", "Test");

        `Mail <https://www.openhab.org/addons/bindings/mail/>`_

        .. code-block::

            // New Mail Binding Action
            actions.get("mail", "mail:smtp:mail_thing").sendMail("someone@example.com", "This is the subject", "This is the message")

            // Deprecated due to new Mail Binding Action
            var OPENHAB_CONF = Java.type('java.lang.System').getenv('OPENHAB_CONF');
            load(OPENHAB_CONF + '/automation/lib/javascript/core/actions.js');

            Mail.sendMail("someone@example.com", "This is the subject", "This is the message");

        `Astro <https://www.openhab.org/addons/actions/astro/#astro-actions>`_

        .. code-block::

            var OPENHAB_CONF = Java.type('java.lang.System').getenv('OPENHAB_CONF');
            load(OPENHAB_CONF + '/automation/lib/javascript/core/actions.js');

            var Date = Java.type('java.util.Date')

            // Use the Astro action to get the sunset start time.
            LogAction.logInfo("Rules", "Sunset: {}".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time));

        `MQTT2 <https://www.openhab.org/addons/bindings/mqtt/>`_

        .. code-block::

            // no import needed
            actions.get("mqtt", "mqtt:systemBroker:embedded-mqtt-broker").publishMQTT("test/system/started", "true");

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: Xtend
        `Telegram <https://www.openhab.org/addons/bindings/telegram/>`_

        .. code-block::

            // New Telegram Binding Action
            getActions.get("telegram", "telegram:telegramBot:xxxxx").sendTelegram("MyBot", "Test")

            // Deprecated due to new Telegram Binding
            sendTelegram("MyBot", "Test")

        `Pushover <https://www.openhab.org/addons/actions/pushover/#pushover-actions>`_

        .. code-block::

            sendPushoverMessage(Pushover.pushoverBuilder("Test"))

        `Pushbullet <https://www.openhab.org/addons/bindings/pushbullet/>`_

        .. code-block::

            // New Pushbullet Binding Action
            getActions.get("pushbullet", "pushbullet:bot:r2d2").sendPushbulletNote("someone@example.com", "R2D2 talks here...", "This is the pushed note.")

            // Deprecated due to new Pushbullet Binding
            sendPushbulletNote("someone@example.com", "openHAB", "Test")

        `Mail <https://www.openhab.org/addons/bindings/mail/>`_

        .. code-block::

            // New Mail Binding Action
            getActions.get("mail", "mail:smtp:mail_thing").sendMail("someone@example.com", "This is the subject", "This is the message")

            // Deprecated due to new Mail Binding
            sendMail("someone@example.com", "This is the subject", "This is the message")

        `Astro <https://www.openhab.org/addons/actions/astro/#astro-actions>`_

        .. code-block::

            // Use the Astro action to get the sunset start time.
            logInfo("Sunset: {}".format(getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))

        `MQTT2 <https://www.openhab.org/addons/bindings/mqtt/>`_

        .. code-block::

            getActions.get("mqtt", "mqtt:systemBroker:embedded-mqtt-broker").publishMQTT("test/system/started", "true")
