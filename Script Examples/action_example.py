from core.actions import Astro
from core.log import logging, LOG_PREFIX
from java.util import Date

log = logging.getLogger(LOG_PREFIX + ".action_example")

log.info("Sunrise: [{}]".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))