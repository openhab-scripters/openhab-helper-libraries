from openhab.actions import Astro
from openhab.log import logging
from java.util import Date

logging.getLogger("org.eclipse.smarthome.automation").info(
    "Sunrise: %s", Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time)
