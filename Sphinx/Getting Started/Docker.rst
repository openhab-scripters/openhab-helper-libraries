******
Docker
******

.. tabs::

    .. group-tab:: Python

        This guide is written for openHAB v2.4, at the time of writing, it was Build #1390. To get this build, run ``docker pull openhab/openhab:2.4.0-snapshot-amd64-debian``.
        Once you have openHAB installed and running, you can install Jython as follows (these are the steps I figured out after some trial and error).

        Installation

        #.  Install the `Next-Generation Rule Engine`_ (in Paper UI, go to Add-ons > Misc, find Rule Engine (Experimental), and click "INSTALL".
            Once installed, Jython and the helper libraries can be installed into openHAB.
        #.  Get the files for openhab2-jython:
                
            .. code-block:: bash

                wget https://github.com/openhab-scripters/openhab-helper-libraries/archive/master.zip
                unzip master.zip
                mv openhab-helper-libraries-master/Core/automation /openhab/conf/

            .. note::

                The last ``mv`` is to move the automation directory into the conf directory that's mounted in openHAB at ``/openhab/conf/``.
                If you already have an `automation` directory, manually move over the individual directories.

        #.  Next, get and install the actual Jython binary:

            .. code-block:: bash

                curl http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar -o jython-standalone-2.7.0.jar
                mkdir conf/automation/jython
                mv jython-standalone-2.7.0.jar /openhab/conf/automation/jython/

            Again, the ``conf`` directory above is the directory that's mounted in openHAB.

        #.  Finally, copy over the ``hello_world.py`` script so we can see things happening in the logs.

            .. code-block:: bash

                cp openhab2-jython-master/Script\ Examples/Python/hello_world.py /openhab/conf/automation/jsr223/python/personal

        Docker Environment

        #.  When starting the docker container, include the environment variable as follows:

            .. code-block:: bash

                -e "EXTRA_JAVA_OPTS=-Xbootclasspath/a:/openhab/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/openhab/conf/automation/jython -Dpython.path=/openhab/conf/automation/lib/python"

            Or, if you are using a compose file, include this:

            .. code-block:: bash

                environment:
                EXTRA_JAVA_OPTS: "-Xbootclasspath/a:/openhab/conf/automation/jython/jython-standalone-2.7.0.jar -Dpython.home=/openhab/conf/automation/jython -Dpython.path=/openhab/conf/automation/lib/python"

        #.  Restart openHAB.
            You should see something such as this in the logs:

            .. code-block:: bash

                2018-10-17 02:18:06.704 [INFO ] [.internal.GenericScriptEngineFactory] - Activated scripting support for python

        #.  After a minute or two, this should appear in the logs every 10 seconds or so:

            .. code-block:: bash

                2018-10-17 02:24:40.077 [INFO ] [eclipse.smarthome.model.script.Rules] - JSR223: This is a 'hello world!' from a Jython rule (decorator): Cron

        Building image from Dockerfile

        In the `/Docker/Python/` directory, there is an example Dockerfile which will add Jython support to the given container version.
        It includes a script to enable the `Next-Generation Rule Engine`_ in the addons.cfg and adds necessary entries to ``EXTRA_JAVA_OPTS`` (including setting python.path to ``/openhab/conf/automation/lib/python/``).
        As a user, you only need to add Python scripts and rules to your ``/conf/automation/jsr223/python/personal/`` volume.

        To build a container with jython, simply run

            .. code-block:: bash

                docker build --build-arg OPENHAB_VERSION=2.4.0.M6-amd64-debian .

        Jython will be installed in ``/opt/jython``.
        The installation directory, as well as Jython version, can be set with build args (see the `/Docker/Python/Dockerfile`).

    .. group-tab:: Javascript

        No documentation for a Javascript Docker installation has been prepared.

    .. group-tab:: Groovy

        No documentation for a Javascript Docker installation has been prepared.

.. _Next-Generation Rule Engine: https://www.openhab.org/docs/configuration/rules-ng.html
