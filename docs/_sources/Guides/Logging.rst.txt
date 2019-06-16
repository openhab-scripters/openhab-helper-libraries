*******
Logging
*******

The helper libraries provide several ways to produce log output in openHAB.
This can be useful for providing information or error messages from your scripts to help diagnose issues.
In some of the following examples, the logger can be modified to wherever you want the log to go.
The default logger used in the modules and scripts is 'jsr223.<language name>', which is pulled from the value assigned to the LOG_PREFIX variable in the configuration library.
If this is modified, be sure to `configure your logging <https://www.openhab.org/docs/administration/logging.html#logging-in-openhab>` to include the logger chosen.


Rule Decorator
==============

    The ``rule`` decorator adds a logger attribute to the function or class that it is decorating.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Example Rule")
                @when("System started")
                def example_function(event):
                    example_function.log.info("Example info log")
                    example_function.log.warn("Example warning log")
                    example_function.log.error("Example error log")
                    example_function.log.debug("Example debug log")
                    example_function.log.critical("Example trace log")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.


core.log
========

    It is also possible to create a logger using the ``core.log`` library to be used by all functions in a script or library.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.log import logging, LOG_PREFIX

                logging.debug("Logging example from root logger [DEBUG]: [{}]".format(5 + 5))
                logging.info("Logging example from root logger [INFO]: [{}]".format(5 + 5))
                logging.warning("Logging example from root logger [WARN]: [{}]".format(5 + 5))
                logging.error("Logging example from root logger [ERROR]: [{}]".format(5 + 5))
                logging.critical("Logging example from root logger [TRACE]: [{}]".format(5 + 5))

                logging.getLogger("{}.test_logging_script".format(LOG_PREFIX)).info("Logging example from logger, using text appended to LOG_PREFIX: [{}]".format(5 + 5))

                log = logging.getLogger("{}.test_logging_script".format(LOG_PREFIX))
                log.info("Logging example from logger, using text appended to LOG_PREFIX: [{}]".format(5 + 5))

        .. group-tab:: JavaScript

            The `core.log` does not yet exist for this language.

        .. group-tab:: Groovy

            The `core.log` does not yet exist for this language.


Log Action
==========

    The openHAB log action, as used in the Rules DSL, can be imported and used to write to the logs from a script or rule.
    Since LogAction uses SLF4J, it supports parameterized logging.
    Parameterized logging is beneficial, since the values in the parameterized are not processed unless the logger is visible in the current logging level.
    This means that the complicated logging you do in debug does not affect the performance of your system when the logging level is set to info.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.actions import LogAction

                LogAction.logInfo("EXAMPLE", "Example info log [{}]", 5 + 5)
                LogAction.logWarn("EXAMPLE", "Example warning log [{}]", 5 + 5)
                LogAction.logError("EXAMPLE", "Example error log [{}]", 5 + 5)
                LogAction.logDebug("EXAMPLE", "Example debug log [{}]", 5 + 5)

        .. group-tab:: JavaScript

            .. code-block:: JavaScript

                'use strict';
                var logInfo = Java.type("org.eclipse.smarthome.model.script.actions.LogAction").logInfo;

                logInfo("Rules", "This is a test [{}]", 5 + 5);

        .. group-tab:: Groovy

            .. code-block:: Groovy

                import org.eclipse.smarthome.model.script.actions.LogAction

                def logInfo = LogAction.&logInfo

                logInfo("Rules", "This is a test [{}]", 5 + 5)

        .. group-tab:: Rules DSL

            .. code-block:: Java

                logInfo("EXAMPLE", "Example info log [{}]", 5 + 5)
                logWarn("EXAMPLE", "Example warning log [{}]", 5 + 5)
                logError("EXAMPLE", "Example error log [{}]", 5 + 5)
                logDebug("EXAMPLE", "Example debug log [{}]", 5 + 5)


SLF4J
=====

    As an alternative to using ``core.log``, you can access ``SLF4J`` directly in a similar manner.
    SLF4J supports parameterized logging.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from org.slf4j import LoggerFactory
                from configuration import LOG_PREFIX
                log = LoggerFactory.getLogger("{}.EXAMPLE".format(LOG_PREFIX))

                log.info("Example info log [{}]", 5 + 5)
                log.warn("Example warning log [{}]", 5 + 5)
                log.error("Example error log [{}]", 5 + 5)
                log.debug("Example debug log [{}]", 5 + 5)

        .. group-tab:: JavaScript

            .. group-tab:: JavaScript

                Documentation has not yet been created for this functionality.

        .. group-tab:: Groovy

            .. group-tab:: Groovy

                Documentation has not yet been created for this functionality.
