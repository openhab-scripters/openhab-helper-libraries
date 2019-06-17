*******
Actions
*******

.. warning:: In order to avoid namespace conflicts with the ``actions`` object provided in the default scope, don't use ``import core.actions``.

Use `Core & Cloud Actions <https://www.openhab.org/docs/configuration/actions.html#core-actions>`_
--------------------------------------------------------------------------------------------------------

For ScriptExecution, see :ref:`Guides/But How Do I:Use a timer`.
For LogAction, see :doc:`Logging`.

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

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

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

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO


Use an Addon/Bundle Action
--------------------------

 The binding or Action must be installed.

.. tabs::

    .. group-tab:: Python

        `Telegram <https://www.openhab.org/addons/actions/telegram/#telegram-actions>`_

        .. code-block::

            from core.actions import Telegram
            Telegram.sendTelegram("MyBot", "Test")

        `Mail <https://www.openhab.org/addons/actions/mail/#mail-actions>`_

        .. code-block::

            from core.actions import Mail
            Mail.sendMail("someone@example.com", "This is the subject", "This is the message")

        `Astro <https://www.openhab.org/addons/actions/astro/#astro-actions>`_

        .. code-block::

            from core.actions import Astro
            from core.log import logging, LOG_PREFIX
            from java.util import Date

            log = logging.getLogger("{}.astro_test".format(LOG_PREFIX))

            # Use the Astro action class to get the sunset start time.
            log.info("Sunrise: {}".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))

        `MQTT2 <https://www.openhab.org/addons/bindings/mqtt/>`_

        .. code-block::

            # no import needed
            actions.get("mqtt", "mqtt:systemBroker:embedded-mqtt-broker").publishMQTT("test/system/started", "true");

    .. group-tab:: JavaScript

        .. code-block:: JavaScript

            TODO

    .. group-tab:: Groovy

        .. code-block:: Groovy

            TODO

    .. group-tab:: Rules DSL

        .. code-block:: java

            TODO
