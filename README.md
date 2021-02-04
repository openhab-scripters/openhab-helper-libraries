# Ivan's Updates

I have decided to start maintaining this fork in light of the fact that there seems to be no activity in the main Helper Libraries repo and there is growing demand for updates to, among other things, bring openHAB 3.x support to these libraries.
In the event that the maintainer of the original repo decides to start working on them again, I will work with him to get the changes here merged back into the original.

A list of what has been done will be kept in [this changelog](Ivan's%20Changelog.md).

# Helper Libraries for openHAB Scripted Automation

The documentation is located at https://crazyivan359.github.io/openhab-helper-libraries/index.html.

This repository holds helper libraries for use with openHAB, the new rule engine, and scripted automation.
The main purpose of the helper libraries is to provide a layer of abstraction for simplifying the interaction of scripts and other libraries with openHAB.
The current release of these libraries can be used with [openHAB](http://openhab.org/) 2.4.0 M3 or 2.4.0 S1319 up to 2.5.x.
The one exception is that custom module handlers, including the StartupTrigger, DirectoryTrigger, and OsgiEventTrigger in the Jython helper libraries require openHAB 2.4.0 S1566 or newer.
A previous version of the Jython core libraries that is compatible with earlier versions of openHAB, but with reduced functionality, has been archived to [this branch](https://github.com/OH-Jython-Scripters/openhab2-jython/tree/original_(%3C%3D2.3)).

These works are based on the original contributions of [Steve Bate](https://github.com/steve-bate) ([original Jython repository](https://github.com/steve-bate/openhab-jython)) and [Helmut Lehmeyer](https://github.com/lewie) ([original JavaScript repository](https://github.com/lewie/openhab2-javascript)), for which we are very thankful!  :vulcan_salute:
