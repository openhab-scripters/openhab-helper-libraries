*******
Logging
*******


The helper libraries provide several ways to produce log output in openHAB.
This can be useful for providing information or error messages from your scripts to help diagnose issues.

In the following examples, the logger can be set to log to whatever destination you like.
Replace ``EXAMPLE`` with the log name you want to use.


Rule Decorator
==============

    The ``rule`` decorator provides a logger to the function it is used on to make logging in rules simple.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                @rule("Example Rule")
                def example_function(event):
                    example_function.log.info("Example info log")
                    example_function.log.warn("Example warning log")
                    example_function.log.error("Example error log")
                    example_function.log.debug("Example debug log")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.


Log Module
==========

    It is also possible to create a logger using the ``core.log`` module to be used by all functions in a script.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                # create the logger at the beginning of the file
                from core.log import logging, LOG_PREFIX
                log = logging.getLogger(LOG_PREFIX + ".EXAMPLE")

                # it can then be used anywhere in the file
                log.info("Example info log")
                log.warn("Example warning log")
                log.error("Example error log")
                log.debug("Example debug log")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: Java

                logInfo("EXAMPLE", "Example info log")
                logWarn("EXAMPLE", "Example warning log")
                logError("EXAMPLE", "Example error log")
                logDebug("EXAMPLE", "Example debug log")


Log Action
==========

    The openHAB log action, as used in the Rules DSL, can be imported and used to write to the logs.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                from core.actions import LogAction

                LogAction.logInfo("EXAMPLE", "Example info log")
                LogAction.logWarn("EXAMPLE", "Example warning log")
                LogAction.logError("EXAMPLE", "Example error log")
                LogAction.logDebug("EXAMPLE", "Example debug log")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: Java

                logInfo("EXAMPLE", "Example info log")
                logWarn("EXAMPLE", "Example warning log")
                logError("EXAMPLE", "Example error log")
                logDebug("EXAMPLE", "Example debug log")


slf4j
=====

    As an alternative to using ``core.log``, you can access ``slf4j`` directly in a similar manner.

    .. tabs::

        .. group-tab:: Python

            .. code-block::

                # create the logger at the beginning of the file
                from org.slf4j import LoggerFactory
                from configuration import LOG_PREFIX
                log = LoggerFactory.getLogger(LOG_PREFIX + ".EXAMPLE")

                # it can then be used anywhere in the file
                log.info("Example info log")
                log.warn("Example warning log")
                log.error("Example error log")
                log.debug("Example debug log")

        .. group-tab:: JavaScript

            Decorators have not yet been created for the JavaScript helper libraries.

        .. group-tab:: Groovy

            Decorators have not yet been created for the Groovy helper libraries.

        .. group-tab:: Rules DSL

            .. code-block:: Java

                logInfo("EXAMPLE", "Example info log")
                logWarn("EXAMPLE", "Example warning log")
                logError("EXAMPLE", "Example error log")
                logDebug("EXAMPLE", "Example debug log")
