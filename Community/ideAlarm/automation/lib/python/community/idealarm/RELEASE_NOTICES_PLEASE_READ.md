**If upgrading from previous versions**
Below are important instructions if you are upgrading ideAlarm from a previous version. If you make a new installation you can ignore what follows.

**PLEASE MAKE SURE THAT YOU GO THROUGH ALL STEPS BELOW WHERE IT SAYS "BREAKING CHANGE", DON'T SKIP ANY VERSION**

***Version 3.0.0***
- **BREAKING CHANGE** ideAlarm requires at least [lucid V 1.0.0](https://github.com/OH-Jython-Scripters/lucid).

- **BREAKING CHANGE** if you are using a [custom helper functions script for various alarm events](https://github.com/OH-Jython-Scripters/ideAlarm/wiki/Event-Helpers#custom-helper-functions-for-various-alarm-events) you should revise it so that it's working with the new version of lucid. Please have a look at the [lucid release notices](https://github.com/OH-Jython-Scripters/lucid/blob/master/RELEASE_NOTICES_PLEASE_READ.md) and optionally look at the [example event helpers script](https://github.com/OH-Jython-Scripters/ideAlarm/blob/master/automation/lib/python/idealarm/custom_verbose_example.py)

***Version 2.0.0***
- **BREAKING CHANGE** ideAlarm new dependency: [lucid, an openHAB 2.x jsr223 Jython helper library](https://github.com/OH-Jython-Scripters/lucid)
- Review that you've setup the item groups correctly as [described in wiki](https://github.com/OH-Jython-Scripters/ideAlarm/wiki/First-Installation#define-item-groups-needed-for-persistence).
- Removed dependency of [openhab2-jython](https://github.com/OH-Jython-Scripters/openhab2-jython). (All openhab2-jython functionality that's needed is now found in [lucid](https://github.com/OH-Jython-Scripters/lucid))
- Removed dependency of [mylib](https://github.com/OH-Jython-Scripters/mylib/) (All mylib functionality that's needed is now found in [lucid](https://github.com/OH-Jython-Scripters/lucid))

***Version 1.0.0***
- Added version info string to logging.
- Added ideAlarm function `__version__()`

***Version 0.9.0***
- Initial version.
