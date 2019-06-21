# Helper Libraries for openHAB Scripted Automation

>***
>## <p style="text-align: center;">***** **UNDER CONSTRUCTION** *****</p>
>The openHAB Scripters (formerly OH Jython Scripters) organization and this repository have both recently had name changes, and there has been a directory restructuring to support more languages. 
Javascript libraries are now included, but they require testing and are likely to have frequent updates as the functionality of the Jython libraries are added to them. 
Please report any issues that you find! 
>
>If you have local repositories, you'll need to [update them to point to the new location](https://help.github.com/en/articles/changing-a-remotes-url).
>***

The documentation is now located at https://openhab-scripters.github.io/openhab-helper-libraries/index.html.

The main purpose of the helper libraries is to provide a layer of abstraction to simplify the interaction of scripts with the openHAB Automation API.
These libraries can be used with [openHAB](http://openhab.org/) (2.4M3, S1319, or newer) and the new rule engine. 
The one exception is that custom module handlers, including the StartupTrigger, DirectoryTrigger, and OsgiEventTrigger in the JythonHLs, require S1566 or newer.

A previous version for Jython that is compatible with earlier versions of openHAB, but with reduced functionality, has been archived to [this branch](https://github.com/OH-Jython-Scripters/openhab2-jython/tree/original_(%3C%3D2.3)).


These works are based on the original contributions of Steve Bate, for which we are very thankful!  :vulcan_salute: 