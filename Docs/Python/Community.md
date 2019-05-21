[[Home]](README.md)

## Community

Community submitted packages, modules and scripts provide additional functionality, on top of what is found in the `core` package and scripts.
When choosing to use a solution submitted by the community, the files will need to be copied to the proper directories. 

#### Script: [`esper_example.py`](../../Community/Esper/automation/jsr223/python/community/esper/esper.py.example)
<ul>

Shows an example of using the Esper component.
The `esper` package`000_Esper.py` component script must also be installed.
</ul>

#### Script: [`owm_daily_forecast.py`](../../Community/OpenWeatherMap/automation/jsr223/python/community/openweathermap/owm_daily_forecast.py)
<ul>

Using a free API key, this script will create the Items and groups, and will move the hourly forecast Items into groups that provide a daily forecast.
[Discussed in the forum](https://community.openhab.org/t/openweathermap-daily-forecast-using-the-free-api/62579).
</ul>

#### Script: [`delete_zwave_things.py`](../../Community/Delete%20and%20Rediscover%20Z-Wave%20Things/automation/jsr223/python/community/delete_zwave_things/delete_zwave_things.py)
<ul>

In order to pickup changes to a Thing definition after upgrading a binding, the existing Things need to be deleted and rediscovered. 
With many Things, this is a challenge. 
This script automates the process of deleting all Z-Wave Things and then rediscovering them. 
[Discussed in the forum](https://community.openhab.org/t/rule-for-deleting-and-rediscovering-things/41001).
</ul>

#### Script: [`speak_and_respond.py`](../../Community/Alexa%20Speak%20and%20Respond/automation/jsr223/python/community/speak_and_respond/speak_and_respond.py)
<ul>

This script will parse all Alexa voice commands, and if they match the text in the rule, it will send a command to an Item linked to that Alexa device's TTS Channel. 
For example, I can ask Alexa "Are the doors locked?", and the device that I asked will respond with "all doors are locked" or a list of the unlocked doors. 
Additional phrases can be added.
</ul>