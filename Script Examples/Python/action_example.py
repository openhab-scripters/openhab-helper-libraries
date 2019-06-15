"""
Shows an example of using the `core.actions` module to access an Action.
Requires the Astro action.
"""

from core.actions import Astro
from core.log import logging, LOG_PREFIX
from java.util import Date

log = logging.getLogger("{}.action_example".format(LOG_PREFIX))

log.info("Sunrise: [{}]".format(Astro.getAstroSunsetStart(Date(2017, 7, 25), 38.897096, -77.036545).time))
